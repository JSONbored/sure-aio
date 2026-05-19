# frozen_string_literal: true

# Alpha-only NDJSON route parity importer.
#
# Enhanced NDJSON proof packages can carry nested Transaction.split_lines plus
# Transfer/RejectedTransfer records that point at either full transaction IDs or
# split-line IDs. Until the behavior lands upstream in Sure proper, the alpha AIO
# lane materializes split lines as Sure split child entries so readback/export can
# prove native split and linked-transfer parity instead of relying on notes or sidecars.
module SureAioAlphaRouteParityImporter
  def import_transactions(records)
    records.each do |record|
      data = record["data"] || {}
      old_id = data["id"]

      account = mapped_account_for_route_parity(data["account_id"])
      next unless account

      transaction = Transaction.new(
        category_id: remap_route_parity_id(:categories, data["category_id"]),
        merchant_id: remap_route_parity_id(:merchants, data["merchant_id"]),
        kind: data["kind"].presence || "standard"
      )

      entry = Entry.new(
        account: account,
        date: Date.parse(data["date"].to_s),
        amount: data["amount"].to_d,
        name: data["name"].presence || "Imported transaction",
        currency: data["currency"].presence || account.currency,
        notes: data["notes"],
        excluded: route_parity_boolean(data["excluded"], default: false),
        entryable: transaction
      )
      entry.save!

      attach_route_parity_tags(transaction, data["tag_ids"])

      @created_entries << entry
      @id_mappings[:transactions][old_id] = transaction.id if old_id.present?

      import_route_parity_split_lines(
        parent_entry: entry,
        parent_transaction: transaction,
        parent_source_id: old_id,
        split_lines: data["split_lines"]
      )
    end
  end

  private

    def mapped_account_for_route_parity(source_id)
      account_id = @id_mappings[:accounts][source_id]
      account_id ? @family.accounts.find(account_id) : nil
    end

    def remap_route_parity_id(mapping_key, source_id)
      return nil unless source_id.present?

      @id_mappings[mapping_key][source_id]
    end

    def attach_route_parity_tags(transaction, source_tag_ids)
      Array(source_tag_ids).filter_map { |source_id| @id_mappings[:tags][source_id] }.each do |tag_id|
        transaction.taggings.create!(tag_id: tag_id)
      end
    end

    def import_route_parity_split_lines(parent_entry:, parent_transaction:, parent_source_id:, split_lines:)
      return unless split_lines.is_a?(Array) && split_lines.any?

      split_lines.each_with_index do |raw_split, index|
        split = raw_split.is_a?(Hash) ? raw_split : {}
        split_source_id = split["id"].presence || "#{parent_source_id}:split:#{index + 1}"
        child_transaction = Transaction.new(
          category_id: remap_route_parity_id(:categories, split["category_id"]),
          merchant_id: remap_route_parity_id(:merchants, split["merchant_id"]) || parent_transaction.merchant_id,
          kind: split["kind"].presence || parent_transaction.kind
        )
        child_entry = parent_entry.child_entries.create!(
          account: parent_entry.account,
          date: parent_entry.date,
          amount: split["amount"].to_d,
          name: split["name"].presence || parent_entry.name,
          currency: split["currency"].presence || parent_entry.currency,
          notes: route_parity_split_notes(
            split: split,
            parent_source_id: parent_source_id,
            split_source_id: split_source_id,
            position: index + 1
          ),
          excluded: route_parity_boolean(split["excluded"], default: false),
          entryable: child_transaction
        )

        attach_route_parity_tags(child_transaction, split["tag_ids"])
        @created_entries << child_entry
        @id_mappings[:transactions][split_source_id] = child_transaction.id
        @id_mappings[:transactions]["simpsplit_#{split_source_id}"] = child_transaction.id
      end

      parent_entry.update!(excluded: true)
    end

    def route_parity_split_notes(split:, parent_source_id:, split_source_id:, position:)
      notes = split["notes"].presence
      parts = [
        notes,
        notes.to_s.include?("Source Split Parent Tx ID:") ? nil : "Source Split Parent Tx ID: #{parent_source_id}",
        notes.to_s.include?("Source Split Line ID:") ? nil : "Source Split Line ID: #{split_source_id}",
        notes.to_s.include?("simplifi:split_position:") ? nil : "simplifi:split_position: #{position}"
      ].compact
      parts.join(" | ")
    end

    def route_parity_boolean(value, default:)
      return default if value.nil?

      ActiveModel::Type::Boolean.new.cast(value)
    end
end

module SureAioAlphaRouteParitySureImport
  def import!
    importer = Family::DataImporter.new(family, ndjson_blob_string)
    result = importer.import!

    bulk_attach_route_parity_import_records(Account, result[:accounts])
    bulk_attach_route_parity_import_records(Entry, result[:entries])
  end

  private

    def bulk_attach_route_parity_import_records(model, records)
      ids = Array(records).filter_map(&:id)
      return if ids.empty?

      model.where(id: ids).in_batches(of: 1000) do |relation|
        relation.update_all(import_id: id)
      end
    end
end

Rails.application.config.to_prepare do
  Family::DataImporter.prepend(SureAioAlphaRouteParityImporter) unless Family::DataImporter < SureAioAlphaRouteParityImporter
  SureImport.prepend(SureAioAlphaRouteParitySureImport) unless SureImport < SureAioAlphaRouteParitySureImport
end
