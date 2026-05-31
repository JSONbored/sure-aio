# Keep Rails' origin comparison enabled by default. Some self-hosted reverse
# proxy/privacy stacks force browsers to send Origin: null; those installs can
# opt out while Rails CSRF token validation remains enabled.
raw_value = ENV.fetch("SURE_CSRF_ORIGIN_CHECK", "true").to_s.strip
normalized_value = raw_value.downcase

case normalized_value
when "", "true", "1", "yes", "on"
  Rails.application.config.action_controller.forgery_protection_origin_check = true
when "false", "0", "no", "off"
  Rails.application.config.action_controller.forgery_protection_origin_check = false
else
  Rails.logger.warn(
    "Ignoring invalid SURE_CSRF_ORIGIN_CHECK=#{raw_value.inspect}; " \
    "expected true/false, 1/0, yes/no, or on/off."
  )
  Rails.application.config.action_controller.forgery_protection_origin_check = true
end
