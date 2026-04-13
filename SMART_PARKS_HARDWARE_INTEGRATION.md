# Smart Parks Hardware Integration

## Current Ingestion Endpoint
`POST /api/smart-parks/readings/ingest`

## Expected Payload
```json
{
  "readings": [
    {
      "device_id": "dev-soil-01",
      "metric_key": "soil_moisture_pct",
      "metric_value": 28.4,
      "unit": "%",
      "recorded_at": "2026-04-13T18:00:00Z",
      "source": "hardware",
      "metadata": {
        "gateway_id": "gw-01",
        "uplink_id": "uplink-123"
      }
    }
  ]
}
```

## Supported Metric Keys
- `tree_tilt_deg`
- `tree_bark_temp_c`
- `soil_moisture_pct`
- `soil_npk_index`
- `soil_ph`
- `water_tds_ppm`
- `water_turbidity_ntu`
- `water_dissolved_oxygen_mg_l`

## Behavior
- Unknown devices are ignored instead of rejecting the whole batch.
- Threshold breaches create alerts automatically.
- Critical breaches create alerts and work orders automatically.
- Device `last_seen_at` is updated on every accepted reading.

## Recommended Gateway Flow
1. Sensor node sends uplink to LoRaWAN gateway.
2. Gateway middleware converts uplink to normalized metrics.
3. Middleware batches readings and posts to Helix.
4. Helix stores telemetry, updates device state, and opens alerts.

## Temporary Development Option
Use:
`POST /api/smart-parks/simulate`

This generates realistic seeded telemetry for demos before hardware is connected.
