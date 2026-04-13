import React, { startTransition, useEffect, useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import { Activity, AlertTriangle, RadioTower, ShieldCheck, Trees, Waves, Wrench } from 'lucide-react';
import { smartParksAPI } from '../api/client';

const defaultWorkOrder = {
  park_id: '',
  title: '',
  description: '',
  priority: 'watch',
  assigned_to: '',
};

const SmartParksWorkspace = () => {
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState('');
  const [dashboard, setDashboard] = useState(null);
  const [report, setReport] = useState(null);
  const [workOrderForm, setWorkOrderForm] = useState(defaultWorkOrder);

  const summary = dashboard?.summary;
  const parks = dashboard?.parks || [];
  const devices = dashboard?.devices || [];
  const alerts = dashboard?.alerts || [];
  const workOrders = dashboard?.work_orders || [];
  const readings = dashboard?.readings || [];
  const parkRisks = dashboard?.park_risks || [];

  const latestReadings = useMemo(() => readings.slice(0, 8), [readings]);

  useEffect(() => {
    loadWorkspace();
  }, []);

  useEffect(() => {
    if (!workOrderForm.park_id && parks[0]) {
      setWorkOrderForm((current) => ({ ...current, park_id: parks[0].id }));
    }
  }, [parks, workOrderForm.park_id]);

  async function loadWorkspace() {
    setLoading(true);
    try {
      const [dashboardRes, reportRes] = await Promise.allSettled([
        smartParksAPI.getDashboard(),
        smartParksAPI.getReportOverview(),
      ]);
      startTransition(() => {
        setDashboard(dashboardRes.status === 'fulfilled' ? dashboardRes.value.data : null);
        setReport(reportRes.status === 'fulfilled' ? reportRes.value.data : null);
      });
      setNotice(dashboardRes.status === 'rejected' ? 'Smart Parks backend is not reachable yet.' : '');
    } catch (error) {
      setNotice('Smart Parks backend is not reachable yet.');
      toast.error(readError(error, 'Failed to load Smart Parks workspace'));
    } finally {
      setLoading(false);
    }
  }

  async function refreshWorkspace() {
    try {
      const response = await smartParksAPI.getDashboard();
      setDashboard(response.data);
    } catch (error) {
      toast.error(readError(error, 'Failed to refresh Smart Parks data'));
    }
  }

  async function handleSimulate() {
    try {
      const response = await smartParksAPI.simulate({ ticks: 1 });
      toast.success(`Simulated ${response.data.readings_created} readings`);
      await loadWorkspace();
    } catch (error) {
      toast.error(readError(error, 'Simulation failed'));
    }
  }

  async function handleAcknowledge(alertId) {
    try {
      await smartParksAPI.acknowledgeAlert(alertId);
      toast.success('Alert acknowledged');
      await refreshWorkspace();
    } catch (error) {
      toast.error(readError(error, 'Failed to acknowledge alert'));
    }
  }

  async function handleResolve(alertId) {
    try {
      await smartParksAPI.resolveAlert(alertId);
      toast.success('Alert resolved');
      await loadWorkspace();
    } catch (error) {
      toast.error(readError(error, 'Failed to resolve alert'));
    }
  }

  async function handleWorkOrderSubmit(event) {
    event.preventDefault();
    if (!workOrderForm.park_id || !workOrderForm.title.trim()) {
      toast.error('Park and title are required');
      return;
    }
    try {
      await smartParksAPI.createWorkOrder(workOrderForm);
      setWorkOrderForm((current) => ({ ...defaultWorkOrder, park_id: current.park_id }));
      toast.success('Work order created');
      await loadWorkspace();
    } catch (error) {
      toast.error(readError(error, 'Failed to create work order'));
    }
  }

  if (loading) {
    return <div className="pt-28 px-6 text-center text-text-secondary">Loading Smart Parks workspace...</div>;
  }

  return (
    <div className="pt-20 bg-[radial-gradient(circle_at_top_left,_rgba(109,170,118,0.18),_transparent_26%),radial-gradient(circle_at_bottom_right,_rgba(45,110,145,0.16),_transparent_24%),linear-gradient(180deg,_#f5f1e7_0%,_#eef5ee_44%,_#f9fbf8_100%)]">
      <section className="px-6 py-16">
        <div className="mx-auto max-w-7xl space-y-10">
          <div className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr]">
            <div className="space-y-5">
              <div className="inline-flex items-center gap-2 rounded-full border border-[#3f6b54]/10 bg-white/70 px-4 py-2 text-[11px] font-bold uppercase tracking-[0.24em] text-[#35553f]">
                <Trees className="h-3.5 w-3.5" />
                <span>Live Smart Parks Segment</span>
              </div>
              <h1 className="text-5xl font-black leading-[0.94] tracking-[-0.04em] text-[#1f3527] md:text-7xl">
                Helix for sensor-first
                <span className="block text-[#2c7287]">urban park operations.</span>
              </h1>
              <p className="max-w-2xl text-base leading-8 text-[#43534a] md:text-lg">
                This workspace is backed by live Smart Parks APIs: seeded pilot parks, device inventory, telemetry ingestion,
                simulation, alerting, work orders, and reporting.
              </p>
              {notice ? <div className="rounded-2xl border border-[#bfa98b]/30 bg-[rgba(191,169,139,0.12)] px-4 py-3 text-sm text-text-secondary">{notice}</div> : null}
              <div className="flex flex-wrap gap-3">
                <button type="button" onClick={handleSimulate} className="btn-solace-primary">Run Simulation Tick</button>
                <button type="button" onClick={loadWorkspace} className="btn-solace-outline">Refresh Data</button>
              </div>
            </div>

            <div className="rounded-[2rem] border border-[#23452f]/8 bg-[linear-gradient(180deg,_rgba(255,255,255,0.78),_rgba(244,251,245,0.72))] p-6 shadow-[0_20px_80px_rgba(54,76,56,0.10)]">
              <div className="grid grid-cols-2 gap-3">
                <MetricCard label="Pilot Parks" value={summary?.park_count || 0} icon={Trees} />
                <MetricCard label="Device Nodes" value={summary?.device_count || 0} icon={RadioTower} />
                <MetricCard label="Open Alerts" value={summary?.active_alerts || 0} icon={AlertTriangle} />
                <MetricCard label="Readiness" value={`${summary?.readiness_score || 0}%`} icon={ShieldCheck} />
              </div>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
            <Panel title="Park Signals" icon={Activity}>
              <div className="grid gap-4 md:grid-cols-3">
                {parkRisks.map((risk) => (
                  <div key={risk.park_id} className="rounded-[1.5rem] border border-[#203f2a]/8 bg-[#1f3d2d] p-5 text-white">
                    <div className="text-lg font-bold">{risk.park_name}</div>
                    <div className="mt-4 grid grid-cols-3 gap-2">
                      <RiskPill label="Tree" value={risk.latest_tree_risk} />
                      <RiskPill label="Soil" value={risk.latest_soil_risk} />
                      <RiskPill label="Water" value={risk.latest_water_risk} />
                    </div>
                    <div className="mt-3 text-sm text-white/80">{risk.latest_note}</div>
                  </div>
                ))}
              </div>
            </Panel>

            <Panel title="Pilot Report" icon={Waves}>
              <div className="grid grid-cols-2 gap-3">
                <SmallMetric label="Total Alerts" value={report?.total_alerts || 0} />
                <SmallMetric label="Resolved" value={report?.resolved_alerts || 0} />
                <SmallMetric label="Avg Battery" value={report?.average_battery_level || 0} />
                <SmallMetric label="Unresolved" value={report?.unresolved_alerts || 0} />
              </div>
            </Panel>
          </div>

          <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
            <Panel title="Alerts" icon={AlertTriangle}>
              <div className="space-y-3">
                {alerts.slice(0, 6).map((alert) => (
                  <div key={alert.id} className="rounded-2xl border border-black/5 bg-white/80 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="text-sm font-bold text-text-primary">{alert.title}</div>
                        <div className="mt-1 text-xs text-text-muted">{alert.metric_key} • {alert.status}</div>
                      </div>
                      <RiskBadge value={alert.severity} />
                    </div>
                    <div className="mt-3 text-sm text-text-secondary">{alert.message}</div>
                    <div className="mt-4 flex gap-2">
                      {alert.status === 'open' ? <button type="button" onClick={() => handleAcknowledge(alert.id)} className="btn-solace-outline !py-2 !px-4 text-xs">Acknowledge</button> : null}
                      {alert.status !== 'resolved' ? <button type="button" onClick={() => handleResolve(alert.id)} className="btn-solace-primary !py-2 !px-4 text-xs">Resolve</button> : null}
                    </div>
                  </div>
                ))}
              </div>
            </Panel>

            <Panel title="Work Orders" icon={Wrench}>
              <form onSubmit={handleWorkOrderSubmit} className="rounded-3xl border border-black/5 bg-[rgba(255,252,247,0.72)] p-5 space-y-4">
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-[0.18em] text-text-muted">Park</label>
                    <select value={workOrderForm.park_id} onChange={(event) => updateField(setWorkOrderForm, 'park_id', event.target.value)} className="input-solace !px-4 !py-3">
                      {parks.map((park) => <option key={park.id} value={park.id}>{park.name}</option>)}
                    </select>
                  </div>
                  <Input label="Assigned To" value={workOrderForm.assigned_to} onChange={(value) => updateField(setWorkOrderForm, 'assigned_to', value)} />
                </div>
                <Input label="Title" value={workOrderForm.title} onChange={(value) => updateField(setWorkOrderForm, 'title', value)} />
                <Textarea label="Description" value={workOrderForm.description} onChange={(value) => updateField(setWorkOrderForm, 'description', value)} />
                <div className="grid gap-3 md:grid-cols-[1fr_auto]">
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-[0.18em] text-text-muted">Priority</label>
                    <select value={workOrderForm.priority} onChange={(event) => updateField(setWorkOrderForm, 'priority', event.target.value)} className="input-solace !px-4 !py-3">
                      <option value="watch">Watch</option>
                      <option value="warning">Warning</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                  <button type="submit" className="btn-solace-primary !py-3 !px-5 self-end">Create Work Order</button>
                </div>
              </form>
              <div className="mt-5 space-y-3">
                {workOrders.slice(0, 5).map((order) => (
                  <div key={order.id} className="rounded-2xl border border-black/5 bg-white/80 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-bold text-text-primary">{order.title}</div>
                      <RiskBadge value={order.priority} />
                    </div>
                    <div className="mt-2 text-sm text-text-secondary">{order.description || 'No description added.'}</div>
                  </div>
                ))}
              </div>
            </Panel>
          </div>

          <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
            <Panel title="Device Inventory" icon={RadioTower}>
              <div className="grid gap-3 md:grid-cols-2">
                {devices.slice(0, 8).map((device) => (
                  <div key={device.id} className="rounded-2xl border border-black/5 bg-white/80 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-bold text-text-primary">{device.name}</div>
                      <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-text-muted">{device.status}</span>
                    </div>
                    <div className="mt-2 text-xs text-text-muted">{device.device_type} • {device.connectivity}</div>
                    <div className="mt-3 text-sm text-text-secondary">Battery: {device.battery_level || 0}%</div>
                  </div>
                ))}
              </div>
            </Panel>

            <Panel title="Latest Telemetry" icon={Activity}>
              <div className="space-y-3">
                {latestReadings.map((reading) => (
                  <div key={reading.id} className="rounded-2xl border border-black/5 bg-white/80 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-sm font-bold text-text-primary">{reading.metric_key}</div>
                      <RiskBadge value={reading.risk_level} />
                    </div>
                    <div className="mt-2 text-sm text-text-secondary">
                      {reading.metric_value} {reading.unit} • {new Date(reading.recorded_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </Panel>
          </div>
        </div>
      </section>
    </div>
  );
};

const Panel = ({ title, icon: Icon, children }) => (
  <div className="glass-card p-6 md:p-7">
    <div className="flex items-center gap-3 mb-5">
      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/70 border border-black/5">
        <Icon className="w-5 h-5 text-solace-purple" />
      </div>
      <h2 className="text-xl font-bold text-text-primary">{title}</h2>
    </div>
    {children}
  </div>
);

const MetricCard = ({ label, value, icon: Icon }) => (
  <div className="rounded-3xl border border-[#213c28]/8 bg-white/80 p-4">
    <div className="flex items-center justify-between gap-3">
      <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#69766d]">{label}</div>
      <Icon className="h-4 w-4 text-[#2f7287]" />
    </div>
    <div className="mt-3 text-3xl font-black tracking-[-0.04em] text-[#20382a]">{value}</div>
  </div>
);

const SmallMetric = ({ label, value }) => (
  <div className="rounded-2xl border border-black/5 bg-white/80 px-4 py-4">
    <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-text-muted">{label}</div>
    <div className="mt-2 text-xl font-bold text-text-primary">{value}</div>
  </div>
);

const RiskPill = ({ label, value }) => (
  <div className={`rounded-2xl px-3 py-3 text-center ${toneForRisk(value)}`}>
    <div className="text-[10px] font-bold uppercase tracking-[0.18em]">{label}</div>
    <div className="mt-1 text-sm font-bold">{value}</div>
  </div>
);

const RiskBadge = ({ value }) => <span className={`rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.16em] ${toneForRisk(value)}`}>{value}</span>;

const Input = ({ label, value, onChange }) => (
  <div className="space-y-2">
    <label className="text-xs font-bold uppercase tracking-[0.18em] text-text-muted">{label}</label>
    <input value={value} onChange={(event) => onChange(event.target.value)} className="input-solace !px-4 !py-3" />
  </div>
);

const Textarea = ({ label, value, onChange }) => (
  <div className="space-y-2">
    <label className="text-xs font-bold uppercase tracking-[0.18em] text-text-muted">{label}</label>
    <textarea value={value} onChange={(event) => onChange(event.target.value)} rows={4} className="input-solace !px-4 !py-3 resize-y min-h-[120px]" />
  </div>
);

function toneForRisk(value) {
  if (value === 'critical') return 'bg-[#863a3a]/70 text-[#ffdede]';
  if (value === 'warning' || value === 'watch') return 'bg-[#7a5a23]/60 text-[#ffe8b0]';
  return 'bg-[#295740]/70 text-[#d7ffea]';
}

function updateField(setter, key, value) {
  setter((current) => ({ ...current, [key]: value }));
}

function readError(error, fallback) {
  return error?.response?.data?.detail || error?.message || fallback;
}

export default SmartParksWorkspace;
