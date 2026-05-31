# frozen_string_literal: true

policy = ENV["SURE_REFERRER_POLICY"].to_s.strip
policy = "strict-origin-when-cross-origin" if policy.empty?

allowed_policies = %w[
  no-referrer
  no-referrer-when-downgrade
  origin
  origin-when-cross-origin
  same-origin
  strict-origin
  strict-origin-when-cross-origin
  unsafe-url
]

unless allowed_policies.include?(policy)
  Rails.logger.warn(
    "Ignoring invalid SURE_REFERRER_POLICY=#{policy.inspect}; " \
    "using strict-origin-when-cross-origin"
  )
  policy = "strict-origin-when-cross-origin"
end

Rails.application.config.action_dispatch.default_headers["Referrer-Policy"] = policy
