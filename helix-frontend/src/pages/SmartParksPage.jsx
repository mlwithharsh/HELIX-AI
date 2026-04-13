import React from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BadgeIndianRupee,
  Droplets,
  Leaf,
  MapPinned,
  RadioTower,
  ShieldCheck,
  Sprout,
  Trees,
  Waves,
} from 'lucide-react';

const pilotStats = [
  { label: 'Pilot Parks', value: '3', icon: MapPinned },
  { label: 'Sensor Nodes', value: '35+', icon: RadioTower },
  { label: 'Committed Spend', value: '6.86L', icon: BadgeIndianRupee },
  { label: 'Deploy Window', value: '90 Days', icon: ShieldCheck },
];

const sensorStacks = [
  {
    title: 'Tree Health',
    icon: Trees,
    description: 'Dendrometers, tilt monitoring, and bark temperature for early structural stress detection.',
    items: ['Growth and stress tracking', 'Instability alerts before visible failure', 'Satellite NDVI validation'],
  },
  {
    title: 'Soil Quality',
    icon: Sprout,
    description: 'Continuous NPK, moisture, pH, EC, and soil temperature sensing at park level.',
    items: ['Sapling survival baselines', 'Nutrient imbalance detection', 'Localized irrigation planning'],
  },
  {
    title: 'Water Quality',
    icon: Droplets,
    description: 'Pond health telemetry with pH, dissolved oxygen, turbidity, and conductivity.',
    items: ['Algae and sediment alerts', 'Water contamination trend lines', 'Reactive inspections replaced by live monitoring'],
  },
];

const parkSignals = [
  {
    park: 'Nehru Ridge Pilot',
    treeRisk: 'Elevated',
    soil: 'Stable',
    water: 'Watch',
    note: 'Tilt variance crossed threshold on two mature trees after recent rain.',
  },
  {
    park: 'Dwarka Sector Green',
    treeRisk: 'Stable',
    soil: 'Action Needed',
    water: 'Stable',
    note: 'Moisture and NPK readings suggest weak retention around fresh plantation zones.',
  },
  {
    park: 'Yamuna Biodiversity Edge',
    treeRisk: 'Stable',
    soil: 'Stable',
    water: 'Critical',
    note: 'TDS and turbidity are trending upward; dissolved oxygen is approaching alert floor.',
  },
];

const rolloutPhases = [
  {
    phase: 'Phase 1',
    title: 'Pilot',
    timeline: 'Months 1-6',
    summary: 'Deploy all three sensor categories across 3 parks and establish the first 12-month baseline.',
  },
  {
    phase: 'Phase 2',
    title: 'Validate + Expand',
    timeline: 'Months 7-18',
    summary: 'Refine thresholds, connect maintenance workflows, and scale to 8-10 parks.',
  },
  {
    phase: 'Phase 3',
    title: 'City Scale',
    timeline: 'Years 2-3',
    summary: 'Extend to 1,000+ parks with predictive scoring and a central command dashboard.',
  },
];

const architectureLayers = [
  {
    label: 'Sense',
    value: 'Tree, soil, and water field nodes',
  },
  {
    label: 'Transmit',
    value: 'LoRaWAN with NB-IoT fallback',
  },
  {
    label: 'Process',
    value: 'ChirpStack and MQTT bridge',
  },
  {
    label: 'Display',
    value: 'ThingsBoard real-time dashboard',
  },
];

const SmartParksPage = () => {
  return (
    <div className="pt-20 bg-[radial-gradient(circle_at_top_left,_rgba(109,170,118,0.18),_transparent_26%),radial-gradient(circle_at_bottom_right,_rgba(45,110,145,0.16),_transparent_24%),linear-gradient(180deg,_#f5f1e7_0%,_#eef5ee_44%,_#f9fbf8_100%)]">
      <section className="relative overflow-hidden px-6 py-16 md:py-24">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute left-[8%] top-16 h-44 w-44 rounded-full bg-[#6d9f67]/18 blur-3xl" />
          <div className="absolute right-[10%] top-24 h-56 w-56 rounded-full bg-[#3f879e]/14 blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-7xl">
          <div className="grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
            <div className="space-y-7">
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.45 }}
                className="inline-flex items-center gap-2 rounded-full border border-[#3f6b54]/10 bg-white/70 px-4 py-2 text-[11px] font-bold uppercase tracking-[0.24em] text-[#35553f]"
              >
                <Leaf className="h-3.5 w-3.5" />
                <span>New Segment: Smart Parks</span>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.05 }}
                className="space-y-5"
              >
                <h1 className="max-w-4xl text-5xl font-black leading-[0.94] tracking-[-0.04em] text-[#1f3527] md:text-7xl">
                  Urban park telemetry,
                  <span className="block text-[#2c7287]">integrated into Helix.</span>
                </h1>
                <p className="max-w-2xl text-base leading-8 text-[#43534a] md:text-lg">
                  This segment turns the DDA Smart Parks pitch into an operator-facing Helix surface: park health signals,
                  sensor architecture, pilot economics, and rollout planning in one workspace.
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="flex flex-wrap gap-3"
              >
                <a href="#park-signals" className="btn-solace-primary flex items-center gap-2">
                  <span>View Pilot Signals</span>
                  <ArrowRight className="h-4 w-4" />
                </a>
                <a href="#architecture" className="btn-solace-outline">
                  Review Architecture
                </a>
              </motion.div>
            </div>

            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.12 }}
              className="rounded-[2rem] border border-[#23452f]/8 bg-[linear-gradient(180deg,_rgba(255,255,255,0.78),_rgba(244,251,245,0.72))] p-6 shadow-[0_20px_80px_rgba(54,76,56,0.10)] backdrop-blur"
            >
              <div className="mb-6 flex items-center justify-between gap-4">
                <div>
                  <div className="text-xs font-bold uppercase tracking-[0.2em] text-[#5a6d60]">Pilot Brief</div>
                  <div className="mt-2 text-2xl font-bold text-[#20382a]">DDA Smart Parks Initiative</div>
                </div>
                <div className="rounded-2xl bg-[#214f39] px-4 py-3 text-right text-white">
                  <div className="text-[10px] uppercase tracking-[0.18em] text-white/70">Budget</div>
                  <div className="text-xl font-bold">10L</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {pilotStats.map(({ label, value, icon: Icon }) => (
                  <div key={label} className="rounded-3xl border border-[#213c28]/8 bg-white/80 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#69766d]">{label}</div>
                      <Icon className="h-4 w-4 text-[#2f7287]" />
                    </div>
                    <div className="mt-3 text-3xl font-black tracking-[-0.04em] text-[#20382a]">{value}</div>
                  </div>
                ))}
              </div>

              <div className="mt-5 rounded-3xl border border-[#b8d4bf]/40 bg-[#edf5ed] p-4 text-sm leading-7 text-[#415247]">
                LoRaWAN-first sensing with local data ownership, zero licensing cost on the dashboard layer, and a rollout path from
                3 parks to city-scale monitoring.
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      <section className="px-6 pb-10">
        <div className="mx-auto grid max-w-7xl gap-6 md:grid-cols-3">
          {sensorStacks.map(({ title, description, items, icon: Icon }) => (
            <div key={title} className="rounded-[1.75rem] border border-[#264532]/8 bg-white/70 p-6 shadow-[0_14px_36px_rgba(42,67,45,0.06)]">
              <div className="flex items-center justify-between gap-3">
                <div className="rounded-2xl bg-[#edf5ed] p-3">
                  <Icon className="h-5 w-5 text-[#21543d]" />
                </div>
                <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#768178]">Sensor Layer</span>
              </div>
              <h2 className="mt-5 text-2xl font-bold text-[#20382a]">{title}</h2>
              <p className="mt-3 text-sm leading-7 text-[#4b5c52]">{description}</p>
              <div className="mt-5 space-y-3">
                {items.map((item) => (
                  <div key={item} className="rounded-2xl bg-[#f6faf6] px-4 py-3 text-sm text-[#385043]">
                    {item}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section id="park-signals" className="px-6 py-12">
        <div className="mx-auto max-w-7xl rounded-[2rem] border border-[#203f2a]/8 bg-[linear-gradient(180deg,_rgba(25,52,38,0.94),_rgba(30,65,47,0.92))] p-6 md:p-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="text-xs font-bold uppercase tracking-[0.22em] text-[#a9d0b1]">Pilot Monitoring</div>
              <h2 className="mt-3 text-3xl font-bold text-white">Live-style park signal board</h2>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/6 px-4 py-3 text-sm text-white/80">
              Demo segment scaffold based on the DDA pitch. Backend telemetry routes are not wired yet.
            </div>
          </div>

          <div className="mt-8 grid gap-4 lg:grid-cols-3">
            {parkSignals.map((signal) => (
              <div key={signal.park} className="rounded-[1.5rem] border border-white/10 bg-white/6 p-5 text-white backdrop-blur">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="text-lg font-bold">{signal.park}</div>
                    <div className="mt-1 text-xs uppercase tracking-[0.18em] text-white/50">Sensor Cluster Status</div>
                  </div>
                  <Activity className="h-5 w-5 text-[#8fd0c7]" />
                </div>

                <div className="mt-5 grid grid-cols-3 gap-3">
                  <SignalPill label="Tree" value={signal.treeRisk} />
                  <SignalPill label="Soil" value={signal.soil} />
                  <SignalPill label="Water" value={signal.water} />
                </div>

                <div className="mt-5 rounded-2xl bg-black/16 px-4 py-4 text-sm leading-7 text-white/78">
                  {signal.note}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="architecture" className="px-6 py-10">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-6 lg:grid-cols-[0.92fr_1.08fr]">
            <div className="rounded-[1.9rem] border border-[#203f2a]/8 bg-white/75 p-6">
              <div className="text-xs font-bold uppercase tracking-[0.2em] text-[#6a776f]">Architecture</div>
              <h2 className="mt-3 text-3xl font-bold text-[#20382a]">End-to-end pipeline</h2>
              <div className="mt-6 space-y-4">
                {architectureLayers.map((layer, index) => (
                  <div key={layer.label} className="flex items-center gap-4 rounded-3xl bg-[#f4f8f2] px-4 py-4">
                    <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#203f2a] text-sm font-bold text-white">
                      {index + 1}
                    </div>
                    <div>
                      <div className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#6f7a72]">{layer.label}</div>
                      <div className="mt-1 text-base font-semibold text-[#263b2d]">{layer.value}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-[1.9rem] border border-[#203f2a]/8 bg-[linear-gradient(180deg,_rgba(255,255,255,0.82),_rgba(240,247,242,0.92))] p-6">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-[#e7f2ea] p-3">
                  <Waves className="h-5 w-5 text-[#286880]" />
                </div>
                <div>
                  <div className="text-xs font-bold uppercase tracking-[0.2em] text-[#6a776f]">Rollout Logic</div>
                  <h2 className="mt-1 text-3xl font-bold text-[#20382a]">Scale path</h2>
                </div>
              </div>

              <div className="mt-6 space-y-4">
                {rolloutPhases.map((item) => (
                  <div key={item.phase} className="rounded-[1.5rem] border border-[#203f2a]/8 bg-white/88 p-5">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="text-sm font-bold uppercase tracking-[0.18em] text-[#2a6d56]">{item.phase}</div>
                      <div className="rounded-full bg-[#edf4ef] px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] text-[#66756c]">
                        {item.timeline}
                      </div>
                    </div>
                    <div className="mt-3 text-xl font-bold text-[#20382a]">{item.title}</div>
                    <p className="mt-2 text-sm leading-7 text-[#4a5a51]">{item.summary}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="px-6 py-12">
        <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="rounded-[1.9rem] border border-[#203f2a]/8 bg-white/78 p-6">
            <div className="flex items-center gap-3">
              <div className="rounded-2xl bg-[#fff5df] p-3">
                <AlertTriangle className="h-5 w-5 text-[#a46d16]" />
              </div>
              <div>
                <div className="text-xs font-bold uppercase tracking-[0.2em] text-[#6d776f]">Problem Frame</div>
                <h2 className="mt-1 text-3xl font-bold text-[#20382a]">Why this segment matters</h2>
              </div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <ProblemCard
                title="Tree failure is invisible"
                description="Internal decay, root stress, and tilt progression are usually detected after visible damage or accident risk."
              />
              <ProblemCard
                title="Soil depletion is silent"
                description="NPK imbalance, compaction, and weak moisture retention reduce sapling survival without any live baseline."
              />
              <ProblemCard
                title="Water contamination is reactive"
                description="Pond quality is often checked only after visible bloom or odour, long after the metrics have shifted."
              />
            </div>
          </div>

          <div className="rounded-[1.9rem] border border-[#203f2a]/8 bg-[#203f2a] p-6 text-white">
            <div className="text-xs font-bold uppercase tracking-[0.22em] text-[#aed0b4]">Operating Notes</div>
            <h2 className="mt-3 text-3xl font-bold">Integration status</h2>
            <div className="mt-6 space-y-4 text-sm leading-7 text-white/82">
              <p>This segment is now available as a first-class Helix route and can be extended the same way the marketing workspace was.</p>
              <p>The next backend step would be a `/api/smart-parks/*` surface for parks, sensors, alerts, and historical telemetry.</p>
              <p>Once those routes exist, this page can switch from pitch-derived demo data to live node status, threshold breaches, and maintenance workflow actions.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

const SignalPill = ({ label, value }) => {
  const tone =
    value === 'Critical'
      ? 'bg-[#863a3a]/70 text-[#ffdede]'
      : value === 'Action Needed' || value === 'Elevated' || value === 'Watch'
        ? 'bg-[#7a5a23]/60 text-[#ffe8b0]'
        : 'bg-[#295740]/70 text-[#d7ffea]';

  return (
    <div className={`rounded-2xl px-3 py-3 text-center ${tone}`}>
      <div className="text-[10px] font-bold uppercase tracking-[0.18em]">{label}</div>
      <div className="mt-1 text-sm font-bold">{value}</div>
    </div>
  );
};

const ProblemCard = ({ title, description }) => (
  <div className="rounded-[1.5rem] bg-[#f7f4ee] p-5">
    <div className="text-base font-bold text-[#22382a]">{title}</div>
    <p className="mt-3 text-sm leading-7 text-[#526158]">{description}</p>
  </div>
);

export default SmartParksPage;
