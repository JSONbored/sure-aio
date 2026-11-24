# frozen_string_literal: true

# The upstream preflight reports existing categories, tags and merchants as
# reusable. This alpha lane requires a clean target before queuing an import.
module SureAioAlphaImportPreflight
  private

  def add_warning(code, message, **details)
    return super unless code == :existing_taxonomy_collision

    add_error(code, message.delete_suffix(" and will be reused.") + ". Import into a clean family.")
  end
end

Rails.application.config.to_prepare do
  unless SureImport::Preflight < SureAioAlphaImportPreflight
    SureImport::Preflight.prepend(SureAioAlphaImportPreflight)
  end
end
