# frozen_string_literal: true

family = Family.create!(name: "Split import fixture", currency: "USD")
accounts = %w[checking wallet].map do |id|
  { type: "Account", data: { id: id, name: id, balance: "500", currency: "USD", accountable_type: "Depository" } }
end
records = accounts + [
  { type: "Transaction", data: {
    id: "atm", account_id: "checking", date: "2026-01-15", amount: "104", name: "Withdrawal",
    split_lines: [
      { id: "cash", name: "Cash portion", amount: "100", notes: "ATM withdrawal" },
      { name: "ATM fee", amount: "4" }
    ]
  } },
  { type: "Transaction", data: {
    id: "wallet-in", account_id: "wallet", date: "2026-01-15", amount: "-100", name: "Wallet deposit"
  } },
  { type: "Transfer", data: {
    id: "cash-transfer", inflow_transaction_id: "wallet-in", outflow_transaction_id: "simpsplit_cash",
    status: "confirmed"
  } }
]

content = records.map(&:to_json).join("\n")
import = SureImport.create!(family: family)
import.ndjson_file.attach(io: StringIO.new(content), filename: "split.ndjson", content_type: "application/x-ndjson")
import.publish
raise "Import failed: #{import.error}" unless import.reload.status == "complete"

parent = family.entries.find_by!(name: "Withdrawal")
cash = parent.child_entries.find_by!(name: "Cash portion")
fee = parent.child_entries.find_by!(name: "ATM fee")
raise "Split parent was counted twice" unless parent.excluded?
raise "Lost supplied notes or source ID" unless cash.notes.include?("ATM withdrawal") && cash.notes.include?("Source Split Line ID: cash")
raise "Lost generated source ID" unless fee.notes.include?("Source Split Line ID: atm:split:2")
raise "Lost import associations" unless [parent, cash, fee].all? { |entry| entry.import_id == import.id }
transfer = Transfer.find_by!(outflow_transaction_id: cash.entryable_id)
raise "Transfer lost its inflow" unless transfer.inflow_transaction.entry.name == "Wallet deposit"
puts "Split import and transfer verified"
