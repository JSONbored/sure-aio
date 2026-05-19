# frozen_string_literal: true

# Alpha-only UI wrapper for the self-hosted financial data reset service.
#
# This keeps the alpha package usable for browser-based import certification
# until the pinned upstream alpha image includes the same Settings UI.
module SureAioAlphaAdminResetUi
  module HostingsControllerPatch
    def financial_data_reset
      load_financial_data_reset_preview
      render layout: financial_data_reset_layout
    end

    def destroy_financial_data_reset
      unless financial_data_reset_confirmed?
        load_financial_data_reset_preview
        @reset_error = t(
          "settings.hostings.destroy_financial_data_reset.confirmation_mismatch",
          phrase: financial_data_reset_confirmation_phrase
        )
        return render :financial_data_reset, status: :unprocessable_entity, layout: financial_data_reset_layout
      end

      @reset_result = Family::FinancialDataReset.new(
        user: Current.user,
        dry_run: false,
        confirmed: true
      ).call

      render :financial_data_reset_complete, layout: financial_data_reset_layout
    end

    private

      def ensure_financial_data_reset_admin
        redirect_to settings_hosting_path, alert: t("settings.hostings.not_authorized") unless Current.user.admin?
      end

      def load_financial_data_reset_preview
        @reset_result = Family::FinancialDataReset.new(user: Current.user).call
        @confirmation_phrase = financial_data_reset_confirmation_phrase
      end

      def financial_data_reset_confirmation_phrase
        Family::FinancialDataReset::CONFIRMATION_PHRASE
      end

      def financial_data_reset_confirmed?
        params[:confirmation].to_s == financial_data_reset_confirmation_phrase
      end

      def financial_data_reset_layout
        turbo_frame_request? ? false : "settings"
      end
  end
end

I18n.backend.store_translations(
  :en,
  settings: {
    hostings: {
      show: {
        reset_financial_data: "Reset financial data",
        reset_financial_data_warning: "Clear this family's accounts, imports, transactions, categories, tags, merchants, rules, budgets, provider items, sync history, and related files while preserving users and authentication records.",
        review_financial_data_reset: "Review reset"
      },
      financial_data_reset: {
        title: "Review financial data reset",
        subtitle: "This reset is scoped to the signed-in family workspace.",
        warning_title: "This permanently deletes financial data",
        warning_body: "Users, passwords, sessions, and authentication settings are preserved. Financial records and import history for this family are deleted after confirmation.",
        scope_title: "Resolved scope",
        user_label: "User",
        family_label: "Family",
        unnamed_family: "Unnamed family",
        counts_title: "Records that will be deleted",
        total_count: "%{count} total records",
        table: {
          target: "Target",
          records: "Records"
        },
        confirmation_label: "Type %{phrase} exactly to continue",
        confirmation_help: "The confirmation is checked by the server before anything is deleted.",
        cancel: "Cancel",
        submit: "Reset financial data"
      },
      destroy_financial_data_reset: {
        confirmation_mismatch: "Type %{phrase} exactly to reset financial data."
      },
      financial_data_reset_complete: {
        title: "Financial data reset complete",
        subtitle: "The selected family workspace has been cleared.",
        success_title: "Reset complete",
        success_message: "Financial and import data was deleted. User and authentication records were preserved.",
        scope_title: "Cleared scope",
        table: {
          before: "Before",
          deleted: "Deleted",
          after: "After"
        },
        close: "Close"
      }
    },
    securities: {
      show: {
        webauthn_mfa_required_title: "Enable 2FA before adding passkeys",
        webauthn_mfa_required_description: "WebAuthn passkeys and security keys are available after authenticator-app 2FA is enabled for this account.",
        webauthn_enable_mfa: "Enable 2FA"
      }
    }
  }
)

Rails.application.routes.append do
  namespace :settings do
    resource :hosting, only: [] do
      get :financial_data_reset, on: :collection
      delete :financial_data_reset, action: :destroy_financial_data_reset, on: :collection
    end
  end
end

Rails.application.config.to_prepare do
  unless Settings::HostingsController < SureAioAlphaAdminResetUi::HostingsControllerPatch
    Settings::HostingsController.prepend(SureAioAlphaAdminResetUi::HostingsControllerPatch)
    Settings::HostingsController.before_action(
      :ensure_financial_data_reset_admin,
      only: %i[financial_data_reset destroy_financial_data_reset]
    )
  end
end
