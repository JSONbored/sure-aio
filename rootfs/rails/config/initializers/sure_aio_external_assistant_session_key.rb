# frozen_string_literal: true

require "digest"

module SureAioExternalAssistantSessionKey
  private

    def build_client
      Assistant::External::Client.new(
        url: self.class.config.url,
        token: self.class.config.token,
        agent_id: self.class.config.agent_id,
        session_key: sure_aio_external_assistant_session_key
      )
    end

    def sure_aio_external_assistant_session_key
      configured = ENV["EXTERNAL_ASSISTANT_SESSION_KEY"].to_s.strip
      return configured if configured.present?

      secret = Rails.application.secret_key_base.to_s
      material = [
        "sure-aio-external-assistant",
        chat&.user&.family_id,
        chat&.user_id,
        chat&.id
      ].join(":")

      "sure-chat:#{Digest::SHA256.hexdigest("#{secret}:#{material}")}"
    end
end

Rails.application.config.to_prepare do
  if defined?(Assistant::External) && !Assistant::External.ancestors.include?(SureAioExternalAssistantSessionKey)
    Assistant::External.prepend(SureAioExternalAssistantSessionKey)
  end
end
