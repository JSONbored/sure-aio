# frozen_string_literal: true

module SureAioAlphaImportLimits
  DEFAULT_NDJSON_SIZE_MB = 250
  DEFAULT_MAX_ROWS = 1_000_000
  MAX_NDJSON_SIZE_MB = 250
  MAX_ROWS = 1_000_000

  module_function

  def capped_positive_integer_env(name, default, maximum)
    value = ENV.fetch(name, "").to_s.strip
    return default if value.empty?

    integer = Integer(value, 10)
    return default unless integer.positive?

    [integer, maximum].min
  rescue ArgumentError
    default
  end

  def max_ndjson_size
    capped_positive_integer_env("SURE_IMPORT_MAX_NDJSON_SIZE_MB", DEFAULT_NDJSON_SIZE_MB, MAX_NDJSON_SIZE_MB).megabytes
  end

  def max_row_count
    capped_positive_integer_env("SURE_IMPORT_MAX_ROWS", DEFAULT_MAX_ROWS, MAX_ROWS)
  end

  def apply!
    SureImport.send(:remove_const, :MAX_NDJSON_SIZE) if SureImport.const_defined?(:MAX_NDJSON_SIZE, false)
    SureImport.const_set(:MAX_NDJSON_SIZE, max_ndjson_size)
    SureImport.define_singleton_method(:max_ndjson_size) { SureImport::MAX_NDJSON_SIZE }
    SureImport.define_singleton_method(:max_row_count) { SureAioAlphaImportLimits.max_row_count }
  end
end

Rails.application.config.to_prepare do
  SureAioAlphaImportLimits.apply!
end
