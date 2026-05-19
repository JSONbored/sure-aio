# frozen_string_literal: true

require "set"

# Alpha-only Sure NDJSON import preflight.
#
# This keeps the current alpha package strict by default while upstream catches
# up: invalid or dirty-target SureImport NDJSON fails before publish/enqueue and
# records the blocking errors on the import for the failure page.
module SureAioAlphaImportPreflight
  IMPORTABLE_NDJSON_TYPES = {
    "Account" => :accounts,
    "Balance" => :balances,
    "Category" => :categories,
    "Tag" => :tags,
    "Merchant" => :merchants,
    "RecurringTransaction" => :recurring_transactions,
    "Transaction" => :transactions,
    "Transfer" => :transfers,
    "RejectedTransfer" => :rejected_transfers,
    "Trade" => :trades,
    "Holding" => :holdings,
    "Valuation" => :valuations,
    "Budget" => :budgets,
    "BudgetCategory" => :budget_categories,
    "Rule" => :rules
  }.freeze

  REQUIRED_FIELDS = {
    "Account" => %w[id name balance accountable_type],
    "Balance" => %w[account_id date balance],
    "Category" => %w[id name],
    "Tag" => %w[id name],
    "Merchant" => %w[id name],
    "RecurringTransaction" => %w[id amount expected_day_of_month last_occurrence_date next_expected_date],
    "Transaction" => %w[id account_id date amount],
    "Transfer" => %w[inflow_transaction_id outflow_transaction_id],
    "RejectedTransfer" => %w[inflow_transaction_id outflow_transaction_id],
    "Trade" => %w[account_id date amount qty price ticker],
    "Holding" => %w[account_id date amount qty price ticker],
    "Valuation" => %w[account_id date amount],
    "Budget" => %w[id start_date end_date],
    "BudgetCategory" => %w[budget_id category_id],
    "Rule" => %w[name]
  }.freeze

  TAXONOMY_TYPES = {
    "Category" => :categories,
    "Tag" => :tags,
    "Merchant" => :merchants
  }.freeze

  SOURCE_ID_TYPES = {
    "Account" => :accounts,
    "Category" => :categories,
    "Tag" => :tags,
    "Merchant" => :merchants,
    "RecurringTransaction" => :recurring_transactions,
    "Transaction" => :transactions,
    "Budget" => :budgets
  }.freeze

  REFERENCE_FIELDS = {
    "Balance" => { accounts: %w[account_id] },
    "Category" => { categories: %w[parent_id] },
    "RecurringTransaction" => { accounts: %w[account_id], merchants: %w[merchant_id] },
    "Transaction" => { accounts: %w[account_id], categories: %w[category_id], merchants: %w[merchant_id] },
    "Transfer" => { transactions: %w[inflow_transaction_id outflow_transaction_id] },
    "RejectedTransfer" => { transactions: %w[inflow_transaction_id outflow_transaction_id] },
    "Trade" => { accounts: %w[account_id] },
    "Holding" => { accounts: %w[account_id] },
    "Valuation" => { accounts: %w[account_id] },
    "BudgetCategory" => { budgets: %w[budget_id], categories: %w[category_id] }
  }.freeze

  Result = Struct.new(:errors, :warnings, :stats, keyword_init: true) do
    def valid?
      errors.empty?
    end

    def error_messages
      errors.map { |error| error[:message] }
    end

    def error_message
      return "" if valid?

      ([ "Sure import preflight failed:" ] + error_messages).join("\n")
    end
  end

  module_function

  def supported_types
    return Family::DataImporter::SUPPORTED_TYPES if defined?(Family::DataImporter::SUPPORTED_TYPES)

    IMPORTABLE_NDJSON_TYPES.keys
  end

  def apply_importable_type_map!
    current = if SureImport.const_defined?(:IMPORTABLE_NDJSON_TYPES, false)
      SureImport::IMPORTABLE_NDJSON_TYPES
    else
      {}
    end
    merged = current.merge(IMPORTABLE_NDJSON_TYPES)

    SureImport.send(:remove_const, :IMPORTABLE_NDJSON_TYPES) if SureImport.const_defined?(:IMPORTABLE_NDJSON_TYPES, false)
    SureImport.const_set(:IMPORTABLE_NDJSON_TYPES, merged.freeze)
  end

  class Preflight
    def initialize(family:, content:)
      @family = family
      @content = content.to_s
      @errors = []
      @warnings = []
      @line_counts = Hash.new(0)
      @records = Hash.new { |hash, key| hash[key] = [] }
      @source_ids = Hash.new { |hash, key| hash[key] = Set.new }
      @rows_count = 0
      @valid_rows_count = 0
    end

    def call
      parse_records
      validate_taxonomy_collisions
      validate_duplicate_taxonomy_names
      validate_required_fields
      validate_accountables
      validate_references
      validate_duplicate_valuations

      Result.new(
        errors: @errors,
        warnings: @warnings,
        stats: {
          rows_count: @rows_count,
          valid_rows_count: @valid_rows_count,
          invalid_rows_count: @rows_count - @valid_rows_count,
          entity_counts: SureImport.dry_run_totals_from_line_type_counts(@line_counts),
          record_type_counts: @line_counts
        }
      )
    end

    private
      attr_reader :family

      def parse_records
        @content.each_line.with_index(1) do |line, line_number|
          next if line.strip.blank?

          @rows_count += 1
          record = JSON.parse(line)

          unless record.is_a?(Hash)
            add_error(:invalid_ndjson_record, "Line #{line_number} must be a JSON object.")
            next
          end

          type = record["type"]
          data = record["data"]

          if type.blank? || !record.key?("data")
            add_error(:invalid_ndjson_record, "Line #{line_number} must include type and data.")
            next
          end

          @line_counts[type] += 1

          unless SureAioAlphaImportPreflight.supported_types.include?(type)
            add_error(:unsupported_record_type, "Line #{line_number} has unsupported record type #{type}.")
            next
          end

          unless data.is_a?(Hash)
            add_error(:invalid_ndjson_record, "Line #{line_number} data must be a JSON object.")
            next
          end

          @valid_rows_count += 1
          @records[type] << { line_number: line_number, data: data }

          mapping_key = SOURCE_ID_TYPES[type]
          @source_ids[mapping_key].add(data["id"].to_s) if mapping_key && data["id"].present?
          add_split_line_source_ids(data) if type == "Transaction"
        rescue JSON::ParserError => e
          add_error(:invalid_json, "Line #{line_number} is not valid JSON: #{e.message}")
        end

        add_error(:no_data_rows, "No data rows were found.") if @rows_count.zero?
      end

      def add_split_line_source_ids(data)
        split_lines = data["split_lines"].presence || data["splitLines"].presence || data["splits"].presence
        Array(split_lines).each do |split_line|
          next unless split_line.is_a?(Hash) && split_line["id"].present?

          @source_ids[:transactions].add(split_line["id"].to_s)
        end
      end

      def validate_taxonomy_collisions
        TAXONOMY_TYPES.each do |type, association|
          existing_names = family.public_send(association).pluck(:name).to_set
          @records[type].each do |record|
            name = record[:data]["name"].to_s
            next if name.blank? || !existing_names.include?(name)

            add_error(
              :existing_taxonomy_collision,
              "Line #{record[:line_number]} #{type} name #{name.inspect} already exists in this family."
            )
          end
        end
      end

      def validate_duplicate_taxonomy_names
        TAXONOMY_TYPES.each_key do |type|
          grouped = @records[type].group_by { |record| record[:data]["name"].to_s }
          grouped.each do |name, records|
            next if name.blank? || records.one?

            lines = records.map { |record| record[:line_number] }.join(", ")
            add_error(
              :duplicate_taxonomy_name,
              "#{type} name #{name.inspect} appears more than once in the NDJSON on lines #{lines}."
            )
          end
        end
      end

      def validate_required_fields
        @records.each do |type, records|
          required_fields = REQUIRED_FIELDS.fetch(type, [])
          records.each do |record|
            missing = required_fields.select { |field| record[:data][field].blank? }
            next if missing.empty?

            add_error(
              :missing_required_fields,
              "Line #{record[:line_number]} #{type} is missing required field(s): #{missing.join(', ')}."
            )
          end
        end
      end

      def validate_accountables
        @records["Account"].each do |record|
          data = record[:data]
          accountable_type = data["accountable_type"].to_s
          unless Accountable::TYPES.include?(accountable_type)
            add_error(
              :invalid_accountable_type,
              "Line #{record[:line_number]} Account has invalid accountable_type #{accountable_type.inspect}."
            )
            next
          end

          accountable = data["accountable"]
          if data.key?("accountable") && accountable.present? && !accountable.is_a?(Hash)
            add_error(
              :invalid_accountable,
              "Line #{record[:line_number]} Account accountable must be a JSON object when provided."
            )
            next
          end

          subtype = accountable.is_a?(Hash) ? accountable["subtype"].presence : nil
          subtype ||= data["subtype"].presence
          next if subtype.blank?

          accountable_class = accountable_type.constantize
          subtype_map = accountable_class.const_defined?(:SUBTYPES) ? accountable_class::SUBTYPES : {}
          next if subtype_map.blank? || subtype_map.key?(subtype)

          add_error(
            :invalid_accountable_subtype,
            "Line #{record[:line_number]} Account has invalid #{accountable_type} subtype #{subtype.inspect}."
          )
        end
      end

      def validate_references
        @records.each do |type, records|
          reference_fields = REFERENCE_FIELDS.fetch(type, {})
          records.each do |record|
            reference_fields.each do |mapping_key, fields|
              fields.each do |field|
                validate_reference(record, type, mapping_key, field, record[:data][field])
              end
            end

            validate_tag_references(record, type)
            validate_split_line_references(record) if type == "Transaction"
          end
        end
      end

      def validate_reference(record, type, mapping_key, field, value)
        return if value.blank?
        return if @source_ids[mapping_key].include?(value.to_s)

        add_error(:missing_reference, "Line #{record[:line_number]} #{type} references missing #{field} #{value.inspect}.")
      end

      def validate_tag_references(record, type)
        Array(record[:data]["tag_ids"]).each do |tag_id|
          validate_reference(record, type, :tags, "tag_ids", tag_id)
        end
      end

      def validate_split_line_references(record)
        split_lines = record[:data]["split_lines"].presence || record[:data]["splitLines"].presence || record[:data]["splits"].presence
        Array(split_lines).each do |split_line|
          next unless split_line.is_a?(Hash)

          validate_reference(record, "Transaction split line", :categories, "category_id", split_line["category_id"])
          validate_reference(record, "Transaction split line", :merchants, "merchant_id", split_line["merchant_id"])
          Array(split_line["tag_ids"]).each do |tag_id|
            validate_reference(record, "Transaction split line", :tags, "tag_ids", tag_id)
          end
        end
      end

      def validate_duplicate_valuations
        seen = {}
        @records["Valuation"].each do |record|
          account_id = record[:data]["account_id"]
          date = record[:data]["date"]
          next if account_id.blank? || date.blank?

          key = [ account_id.to_s, date.to_s ]
          if seen.key?(key)
            add_error(
              :duplicate_valuation,
              "Line #{record[:line_number]} duplicates valuation for account #{account_id.inspect} on #{date}; first seen on line #{seen[key]}."
            )
          else
            seen[key] = record[:line_number]
          end
        end
      end

      def add_error(code, message)
        @errors << { code: code.to_s, message: message }
      end
  end

  module SureImportPatch
    def publish_later
      raise Import::MaxRowCountExceededError if row_count_exceeded?

      validate_sure_preflight!
      raise "Import is not publishable" unless publishable?

      update! status: :importing

      ImportJob.perform_later(self)
    end

    def publish
      raise Import::MaxRowCountExceededError if row_count_exceeded?

      validate_sure_preflight!

      import!
      family.sync_later

      update! status: :complete
    rescue => error
      update! status: :failed, error: error.message
    end

    def sure_preflight
      SureImport::Preflight.new(family: family, content: ndjson_blob_string).call
    end

    private

      def validate_sure_preflight!
        result = sure_preflight
        return if result.valid?

        update! status: :failed, error: result.error_message
        raise SureImport::PreflightError, result.error_message
      end
  end

  module ImportPreflightPatch
    private

      def sure_import_preflight_payload(content, filename, content_type)
        result = SureImport::Preflight.new(family: family, content: content).call
        stats = result.stats
        warnings = result.warnings.dup
        if stats[:rows_count].positive? && stats[:entity_counts].values.sum.zero?
          warnings << "No importable records were found."
        end
        warnings << "Row count exceeds this import type's publish limit." if stats[:rows_count] > SureImport.max_row_count

        {
          type: "SureImport",
          valid: result.valid?,
          content: content_payload(filename, content_type, content),
          stats: stats,
          errors: result.errors,
          warnings: warnings
        }
      end
  end

  module ApiImportsControllerPatch
    def create_sure_import(family)
      content, filename, content_type = sure_import_upload_attributes
      return unless content

      begin
        @import = persist_sure_import!(family, content, filename, content_type)
      rescue ActiveRecord::RecordInvalid => e
        render json: {
          error: "validation_failed",
          message: "Import could not be created",
          errors: e.record&.errors&.full_messages || @import&.errors&.full_messages || []
        }, status: :unprocessable_entity
        return
      rescue StandardError => e
        Rails.logger.error "Sure import creation failed: #{e.message}"
        render json: {
          error: "internal_server_error",
          message: "Import could not be created"
        }, status: :internal_server_error
        return
      end

      begin
        @import.publish_later if params[:publish] == "true"
      rescue Import::MaxRowCountExceededError
        render json: {
          error: "max_row_count_exceeded",
          message: "Import was uploaded but has too many rows to publish automatically.",
          import_id: @import.id
        }, status: :unprocessable_entity
        return
      rescue SureImport::PreflightError
        render json: {
          error: "preflight_failed",
          message: "Import was uploaded but did not pass Sure NDJSON preflight.",
          errors: @import.error.to_s.lines.map(&:strip).reject(&:blank?),
          import_id: @import.id
        }, status: :unprocessable_entity
        return
      rescue StandardError => e
        Rails.logger.error "Sure import publish failed for import #{@import.id}: #{e.message}"
        restore_pending_sure_import_after_publish_failure
        render json: {
          error: "publish_failed",
          message: "Import was uploaded but could not be queued for processing.",
          import_id: @import.id
        }, status: :internal_server_error
        return
      end

      render :show, status: :created
    end

    private :create_sure_import
  end

  module ImportsControllerPatch
    def publish
      super
    rescue SureImport::PreflightError => e
      redirect_to import_path(@import), alert: e.message
    end
  end
end

Rails.application.config.to_prepare do
  SureAioAlphaImportPreflight.apply_importable_type_map!

  unless SureImport.const_defined?(:PreflightError, false)
    SureImport.const_set(:PreflightError, Class.new(StandardError))
  end

  unless SureImport.const_defined?(:Preflight, false)
    SureImport.const_set(:Preflight, SureAioAlphaImportPreflight::Preflight)
  end

  unless SureImport < SureAioAlphaImportPreflight::SureImportPatch
    SureImport.prepend(SureAioAlphaImportPreflight::SureImportPatch)
  end

  unless Import::Preflight < SureAioAlphaImportPreflight::ImportPreflightPatch
    Import::Preflight.prepend(SureAioAlphaImportPreflight::ImportPreflightPatch)
  end

  unless Api::V1::ImportsController < SureAioAlphaImportPreflight::ApiImportsControllerPatch
    Api::V1::ImportsController.prepend(SureAioAlphaImportPreflight::ApiImportsControllerPatch)
  end

  unless ImportsController < SureAioAlphaImportPreflight::ImportsControllerPatch
    ImportsController.prepend(SureAioAlphaImportPreflight::ImportsControllerPatch)
  end
end
