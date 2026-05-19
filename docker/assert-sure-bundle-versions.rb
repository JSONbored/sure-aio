# frozen_string_literal: true

require "bundler"

EXPECTED_GEMS = {
  "rack" => "3.2.6",
  "rack-session" => "2.1.2",
  "addressable" => "2.8.7",
  "rexml" => "3.4.2"
}.freeze

locked_versions = Bundler.locked_gems.specs.each_with_object({}) do |spec, versions|
  versions[spec.name] = spec.version.to_s
end

mismatches = EXPECTED_GEMS.reject do |name, expected|
  locked_versions[name] == expected
end

abort("unexpected upstream gem versions: #{mismatches}") unless mismatches.empty?
