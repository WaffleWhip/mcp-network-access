# WiFi Optimization SOP
MANDATORY: Follow these steps for any WiFi interference issue.
1. Discovery: Run 'ont_get_all_params' first to find the current SSID and radio paths.
2. Trigger: Use 'ont_custom_parameter' to set 'DiagnosticsState' to 'Requested'.
3. Wait: Pause for 45s before reading results.
4. Action: Analyze signal levels and change channel only after verification.
