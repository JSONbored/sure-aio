# The PWA service worker is a public GET asset served by an upstream Rails
# controller as JavaScript. Rails' same-origin JavaScript response guard
# otherwise treats normal browser service-worker registration as a protected
# cross-origin script response and logs ActionController::InvalidCrossOriginRequest.
module SureAioPwaServiceWorkerForgeryGuard
  private

  def verify_same_origin_request
    return if action_name == "service_worker"

    super
  end
end

Rails.application.config.to_prepare do
  controller = "PwaController".safe_constantize
  next unless controller

  controller.prepend SureAioPwaServiceWorkerForgeryGuard
end
