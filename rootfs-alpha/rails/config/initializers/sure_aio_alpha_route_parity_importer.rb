# frozen_string_literal: true

# Keep the source identifiers used by Enhanced NDJSON proof packages while
# Sure owns record creation, retries, session mappings and transfer links.
module SureAioAlphaRouteParityImporter
  private

  def importable_split_rows(data)
    super.each_with_index do |row, index|
      row[:old_id] ||= "#{data.fetch("id")}:split:#{index + 1}"
      notes = row[:notes].to_s
      parts = [notes.presence]
      parts << "Source Split Parent Tx ID: #{data.fetch("id")}" unless notes.include?("Source Split Parent Tx ID:")
      parts << "Source Split Line ID: #{row[:old_id]}" unless notes.include?("Source Split Line ID:")
      parts << "simplifi:split_position: #{index + 1}" unless notes.include?("simplifi:split_position:")
      row[:notes] = parts.compact.join(" | ")
    end
  end

  def import_split_lines!(entry, split_rows, fallback_tag_ids:)
    @route_parity_split_ids = split_rows.pluck(:old_id).to_set
    super
  ensure
    @route_parity_split_ids = nil
  end

  def map_source!(mapping_key, source_id, target)
    super
    if mapping_key == :transactions && @route_parity_split_ids&.include?(source_id)
      super(mapping_key, "simpsplit_#{source_id}", target)
    end
  end
end

module SureAioAlphaSplitPreflight
  private

  def add_split_line_source_ids(data, line_number)
    super
    rows = split_lines_value(data)
    return unless rows.is_a?(Array)

    rows.each_with_index do |row, index|
      next unless row.is_a?(Hash)

      source_id = row["id"].presence || "#{data["id"]}:split:#{index + 1}"
      location = "Line #{line_number} Transaction split line #{index + 1}"
      track_source_id(:transactions, source_id, location) if row["id"].blank?
      track_source_id(:transactions, "simpsplit_#{source_id}", location)
    end
  end
end

Rails.application.config.to_prepare do
  unless Family::DataImporter < SureAioAlphaRouteParityImporter
    Family::DataImporter.prepend(SureAioAlphaRouteParityImporter)
  end
  unless SureImport::Preflight < SureAioAlphaSplitPreflight
    SureImport::Preflight.prepend(SureAioAlphaSplitPreflight)
  end
end
