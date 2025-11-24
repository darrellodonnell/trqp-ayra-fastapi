
DIDs:

TODO:

- [ ] switch to did:web?
- [ ] get list of actual DIDs
- [ ] TEST  

## Demo Sites

* **Ayra Trust Network Trust Registr**y: https://demo-tr.ayra.network/admin/ui

* verifiers.sa.affinidi.io 



## Key DIDs

* Sweetlane Group: did:webvh:SCID-SLGROUP:sweetlane.example.com
* Ayra Trust Network SANDBOX: did:webvh:SCID-ATN:sandbox-tr.ayra.network

API Endpoint: 
* https://sandbox-tr.ayra.network - NOT IN USE (but LIVE)
* https://demo-tr.ayra.network

### ngrok

```
ngrok http --hostname demo-tr.ayra.network 8000
```





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
