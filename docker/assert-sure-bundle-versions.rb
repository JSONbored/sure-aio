# frozen_string_literal: true

require "bundler"

# Each security-sensitive gem maps to the set of upstream versions we have
# reviewed and accept. The stable and alpha base images can pin different patch
# versions of the same gem (e.g. addressable 2.8.7 on the stable base, 2.9.0 on
# the alpha base), so a single exact pin cannot satisfy both lanes. Allowing an
# explicit set keeps the guard as a tripwire for an *unexpected* version while
# tolerating the reviewed divergence between lanes.
EXPECTED_GEMS = {
  "rack" => ["3.2.6"],
  "rack-session" => ["2.1.2"],
  "addressable" => ["2.8.7", "2.9.0"],
  "rexml" => ["3.4.2"]
}.freeze

locked_versions = Bundler.locked_gems.specs.each_with_object({}) do |spec, versions|
  versions[spec.name] = spec.version.to_s
end

mismatches = EXPECTED_GEMS.reject do |name, allowed|
  allowed.include?(locked_versions[name])
end

abort("unexpected upstream gem versions: #{mismatches}") unless mismatches.empty?
