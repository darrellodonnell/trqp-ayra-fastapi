
did:webvh:SCID-SLGROUP:sweetlane.example.com

Ayra Trust Network SANDBOX: did:webvh:SCID-ATN:sandbox-tr.ayra.network

API Endpoint: https://sandbox-tr.ayra.network






## /authorization

Useful query:
```
{
  "entity_id": "did:webvh:SCID-SLBANK:sweetlanebank.example.com",
  "authority_id": "did:webvh:SCID-SLGROUP:sweetlane.example.com",
  "action": "issue",
  "resource": "ayracard:businesscard",
  "context": {
    "time": "2025-11-18T23:19:55.664008Z"
  }
}
```

## /recognition

Useful query:
```
{
  "entity_id": "did:webvh:SCID-SLGROUP:sweetlane.example.com",
  "authority_id": "did:webvh:SCID-ATN:ayra.forum",
  "action": "member-of",
  "resource": "ayratrustnetwork",
  "context": {
    "time": "2025-11-18T23:19:55.664008Z"
  }
}
```
