"""Generate 60 deliberately simple synthetic cases. These are NOT independent gold labels."""
import json
from pathlib import Path

patterns = {
 "diagnostic": [
  ({"contract_mismatch": True},"inspect_contract"), ({"missing_requirement": True},"inspect_contract"),
  ({"source_failure": True},"inspect_source"), ({"regression": True},"inspect_source"),
  ({"runner_error": True},"inspect_runner"), ({"timeout": True},"inspect_runner"),
  ({},"human_review"), ({"policy_flags": ["production_release"],"regression": True},"human_review"),
  ({"policy_flags": ["secret_access"],"runner_error": True},"human_review"),
  ({"approval_required": True,"source_failure": True},"human_review"),
  ({"contract_mismatch": True,"runner_error": True},"inspect_contract"),
  ({"missing_requirement": True,"source_failure": True},"inspect_contract"),
  ({"timeout": True,"source_failure": True},"inspect_runner"),
  ({"policy_flags": ["payment"],"missing_requirement": True},"human_review"),
  ({"unknown_identity": True},"human_review"), ({"source_failure": False},"human_review"),
  ({"regression": True,"contract_mismatch": False},"inspect_source"),
  ({"runner_error": True,"timeout": True},"inspect_runner"),
  ({"policy_flags": ["network_change"],"runner_error": True},"human_review"),
  ({"missing_requirement": True,"timeout": True},"inspect_contract")
 ],
 "partnership": [
  ({"public_source": True},"research"),
  ({"verified_sponsor": True,"written_r0_terms": True},"pilot_review"),
  ({"card_required": True},"reject"), ({"auto_bill": True},"reject"),
  ({"rights_conflict": True},"reject"), ({},"human_review"),
  ({"unknown_identity": True,"public_source": True},"human_review"),
  ({"policy_flags": ["external_send"],"public_source": True},"human_review"),
  ({"policy_flags": ["payment"],"verified_sponsor": True},"human_review"),
  ({"verified_sponsor": True},"human_review"), ({"written_r0_terms": True},"human_review"),
  ({"public_source": True,"card_required": True},"reject"),
  ({"public_source": True,"verified_sponsor": True,"written_r0_terms": True},"pilot_review"),
  ({"approval_required": True,"verified_sponsor": True,"written_r0_terms": True},"human_review"),
  ({"public_source": False},"human_review"),
  ({"rights_conflict": True,"auto_bill": True},"reject"),
  ({"policy_flags": ["unreviewed_customer_data"],"public_source": True},"human_review"),
  ({"public_source": True,"written_r0_terms": False},"research"),
  ({"card_required": False,"verified_sponsor": True,"written_r0_terms": True},"pilot_review"),
  ({"policy_flags": ["employer_data"],"card_required": True},"human_review")
 ],
 "quality": [
  ({"wcag_failure": True},"inspect_accessibility"),
  ({"keyboard_trap": True},"inspect_accessibility"),
  ({"rights_missing": True},"inspect_rights"), ({"asset_unlicensed": True},"inspect_rights"),
  ({"child_safety_flag": True},"inspect_safety"),
  ({"security_flag": True},"inspect_safety"), ({},"human_review"),
  ({"policy_flags": ["production_release"],"wcag_failure": True},"human_review"),
  ({"policy_flags": ["child_data"],"child_safety_flag": True},"human_review"),
  ({"approval_required": True,"asset_unlicensed": True},"human_review"),
  ({"child_safety_flag": True,"wcag_failure": True},"inspect_safety"),
  ({"rights_missing": True,"wcag_failure": True},"inspect_rights"),
  ({"security_flag": True,"asset_unlicensed": True},"inspect_safety"),
  ({"policy_flags": ["deletion"],"rights_missing": True},"human_review"),
  ({"unknown_identity": True},"human_review"), ({"wcag_failure": False},"human_review"),
  ({"keyboard_trap": True,"asset_unlicensed": False},"inspect_accessibility"),
  ({"asset_unlicensed": True,"rights_missing": True},"inspect_rights"),
  ({"policy_flags": ["privacy_review_missing"],"security_flag": True},"human_review"),
  ({"child_safety_flag": True,"rights_missing": True},"inspect_safety")
 ]
}

rows = [
    {"id": f"{wf[:2].upper()}-{i:02d}", "workflow": wf, "state": state,
     "gold": gold, "split": "holdout" if i % 3 == 0 else "development"}
    for wf, group in patterns.items() for i, (state, gold) in enumerate(group, 1)
]
Path(__file__).with_name("fixtures.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {len(rows)} hand-curated synthetic fixture cases")
