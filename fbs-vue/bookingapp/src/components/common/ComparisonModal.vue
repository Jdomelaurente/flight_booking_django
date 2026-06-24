<template>
  <div class="comparison-modal fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm" v-if="isOpen">
    <div class="modal-overlay absolute inset-0" @click="closeModal"></div>
    
    <div class="modal-content relative bg-[#f1f5f9] w-full max-w-6xl max-h-[90vh] flex flex-col rounded-2xl overflow-hidden shadow-2xl animate-in zoom-in">
      
      <!-- Premium Header -->
      <div class="sticky top-0 z-30 bg-white px-8 py-5 flex items-center justify-between border-b border-gray-200">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center text-white shadow-lg shadow-emerald-200/50">
            <i class="ph ph-shield-check text-xl"></i>
          </div>
          <div>
            <h2 class="text-lg font-black text-gray-900 uppercase tracking-tight">Post-Activity Analysis Audit</h2>
            <p class="text-[9px] font-black text-gray-400 uppercase tracking-[0.2em] mt-0.5">{{ activity?.title }} • SECURE ASSESSMENT RECORD</p>
          </div>
        </div>
        <button @click="closeModal" class="w-10 h-10 flex items-center justify-center rounded-xl bg-gray-100 text-gray-400 hover:bg-gray-200 hover:text-gray-900 transition-all">
          <i class="ph ph-x text-xl"></i>
        </button>
      </div>

      <!-- Scrollable Performance Content -->
      <div class="modal-content-scrollable p-8 space-y-8 overflow-y-auto custom-scrollbar">
        
        <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
          <div class="w-12 h-1 bg-gray-200 rounded-full overflow-hidden mb-4">
            <div class="h-full bg-emerald-500 w-1/3 animate-pulse"></div>
          </div>
          <p class="text-xs font-bold text-gray-500 uppercase tracking-widest">Synchronizing Assessment Data...</p>
        </div>

        <div v-else class="space-y-8">
          
          <!-- Top Card: Activity Summary & Score -->
          <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 flex flex-col lg:flex-row gap-10">
            <!-- Left: Activity Info & Score -->
            <div class="flex-1 space-y-6">
              <div>
                <h1 class="text-3xl font-bold mb-1 tracking-tight text-gray-900">{{ activity?.title }}</h1>
                <p class="text-gray-500 font-medium text-sm">Assessment Review • {{ activity?.section_code }}</p>
                <div class="flex flex-wrap gap-2 mt-4">
                  <span class="px-3 py-1 bg-emerald-100 text-emerald-600 text-[9px] font-black rounded-full uppercase tracking-widest border border-emerald-200">
                    Submission Finalized
                  </span>
                  <span v-if="grade !== null" class="px-3 py-1 bg-blue-100 text-blue-600 text-[9px] font-black rounded-full uppercase tracking-widest border border-blue-200">
                    Validated by Instructor
                  </span>
                </div>
              </div>

              <div class="space-y-3">
                <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Final Performance Score:</p>
                <div class="bg-emerald-50 rounded-xl p-8 flex items-center justify-center border border-emerald-100 relative overflow-hidden group">
                  <div class="absolute inset-0 bg-emerald-600 opacity-0 group-hover:opacity-[0.02] transition-opacity"></div>
                  <span class="text-6xl font-black tracking-tighter text-emerald-900">
                    {{ Math.round((calculatedScore / (activity?.total_points || 100)) * 100) }}%
                  </span>
                  <div class="absolute bottom-2 right-4 text-[10px] font-black text-emerald-300 uppercase">
                    {{ calculatedScore.toFixed(0) }} / {{ activity?.total_points }} PTS
                  </div>
                </div>
              </div>

              <!-- Digital Proctor Recommendation -->
              <div class="bg-blue-50 border border-blue-100 rounded-xl p-5 space-y-3">
                 <div class="flex items-center gap-3">
                    <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center text-white shadow-sm">
                       <i class="ph ph-brain text-lg"></i>
                    </div>
                    <h4 class="text-[10px] font-black text-blue-600 uppercase tracking-widest">Digital Proctor Recommendation</h4>
                 </div>
                 <p v-if="!booking" class="text-[11px] text-blue-800 font-bold leading-relaxed">
                    Submission timing expired. We recommend focusing on workflow speed and terminal command efficiency.
                 </p>
                 <p v-else-if="(calculatedScore / (activity?.total_points || 100)) >= 0.9" class="text-[11px] text-blue-800 font-bold leading-relaxed">
                    Outstanding accuracy detected. You have demonstrated mastery of the GDS workflow for this itinerary.
                 </p>
                 <p v-else-if="(calculatedScore / (activity?.total_points || 100)) >= 0.7" class="text-[11px] text-blue-800 font-bold leading-relaxed">
                    Technically sound, but review the passenger data matches. Minor discrepancies in naming or passport info affected the score.
                 </p>
                 <p v-else class="text-[11px] text-blue-800 font-bold leading-relaxed">
                    Critical deviations detected. Review the routing parameters or cabin class selection. Significant non-compliance with instructions found.
                 </p>
              </div>
            </div>

            <!-- Right: Score Breakdown Rubrics (The 5 items) -->
            <div class="w-full lg:w-[450px] bg-gray-50 rounded-2xl border border-gray-100 p-8">
              <h2 class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mb-8">Performance Rubric Breakdown</h2>
              <div class="space-y-6">
                <div v-for="item in rubricBreakdown" :key="item.label" class="space-y-3">
                  <div class="flex justify-between items-end">
                    <div>
                      <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest leading-none mb-1">{{ item.label }}</p>
                      <p class="text-[10px] font-bold text-emerald-600 uppercase">{{ item.status }}</p>
                    </div>
                    <p class="text-sm font-black text-gray-900">
                      Level {{ item.level }}/5
                    </p>
                  </div>
                  <div class="w-full h-2 bg-white rounded-full overflow-hidden flex border border-gray-100 shadow-inner">
                    <div 
                      class="h-full transition-all duration-1000 bg-emerald-500" 
                      :style="{ width: (item.level / 5 * 100) + '%' }"
                    ></div>
                  </div>
                  <p class="text-[9px] text-gray-500 italic">{{ item.description }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Detailed Verification Tables (Rubric Sections) -->
          <div v-for="item in rubricBreakdown" :key="item.label" class="space-y-4">
            <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
              <div class="px-6 py-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                <h3 class="text-[10px] font-black text-gray-900 uppercase tracking-widest">{{ item.label }}</h3>
                <span class="px-2 py-1 bg-emerald-100 text-emerald-700 text-[9px] font-black rounded uppercase">Level {{ item.level }} - {{ item.status }}</span>
              </div>
              <div class="p-6 border-b border-gray-100">
                <p class="text-[13px] text-gray-700 font-medium leading-relaxed">{{ item.description }}</p>
                <div class="flex flex-wrap gap-2 mt-4">
                  <span v-for="tag in item.criteria" :key="tag.label" 
                    class="px-2 py-1 rounded-lg text-[9px] font-black uppercase tracking-wider"
                    :class="tag.isMet ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : 'bg-red-50 text-red-600 border border-red-100'"
                  >
                    {{ tag.label }}
                  </span>
                </div>
              </div>

              <!-- NESTED TABLES -->
              <!-- Accuracy Table -->
              <div v-if="item.label.includes('Accuracy')" class="overflow-x-auto bg-white">
                <table class="w-full border-collapse text-left text-xs uppercase">
                  <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                     <tr>
                       <th class="px-8 py-3">Selection Category</th>
                       <th class="px-8 py-3 text-left">Instruction (Required)</th>
                       <th class="px-8 py-3 text-left">Your Entry (Actual)</th>
                       <th class="px-8 py-3 text-right pr-10">Status</th>
                     </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100 font-bold">
                    <tr v-for="row in routingAuditRows" :key="row.label" 
                        :class="row.isMet ? 'bg-emerald-50/10 text-emerald-800' : 'bg-red-50/10 text-red-800'">
                      <td class="px-8 py-3 text-gray-400">{{ row.label }}</td>
                      <td class="px-8 py-3 uppercase">{{ row.requirement }}</td>
                      <td class="px-8 py-3 uppercase">{{ row.work }}</td>
                      <td class="px-8 py-3 text-right pr-10">{{ row.isMet ? '✓' : '✕' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Technical Skill Table -->
              <div v-if="item.label === 'Technical Skill'" class="overflow-x-auto border-t border-gray-100">
                <table class="w-full border-collapse text-left text-xs uppercase">
                  <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                     <tr>
                       <th class="px-8 py-3">Technical Parameter</th>
                       <th class="px-8 py-3">Requirement</th>
                       <th class="px-8 py-3">Result</th>
                       <th class="px-8 py-3 text-right pr-10">Status</th>
                     </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100 font-bold">
                    <tr v-for="row in techRows" :key="row.label"
                        :class="row.isMet ? 'bg-emerald-50/10 text-emerald-700' : 'bg-red-50/10 text-red-700'">
                      <td class="px-8 py-3 text-gray-400">{{ row.label }}</td>
                      <td class="px-8 py-3">{{ row.requirement }}</td>
                      <td class="px-8 py-3">{{ row.work }}</td>
                      <td class="px-8 py-3 text-right pr-10">{{ row.isMet ? '✓' : '✕' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Organization / Passenger Table -->
              <div v-if="item.label.includes('Organization')" class="border-t border-gray-100">
                <div v-for="(p, idx) in matches.passenger_details" :key="idx" class="border-b last:border-0 border-gray-100">
                  <div class="px-8 py-3 bg-gray-50/30 flex justify-between items-center">
                    <span class="text-[9px] font-black text-gray-500 uppercase tracking-[0.2em]">Identity Profile {{ idx + 1 }}: {{ p.name.actual }}</span>
                    <span class="text-[9px] font-black uppercase px-2 py-0.5 rounded"
                      :class="isPassengerSectionMet(p) ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600'">
                      {{ isPassengerSectionMet(p) ? 'SYNCED' : 'DATA GAP' }}
                    </span>
                  </div>
                  <div class="overflow-x-auto">
                    <table class="w-full border-collapse text-[10px] uppercase">
                      <tbody class="divide-y divide-gray-50 font-bold">
                        <tr v-for="(val, field) in p" :key="field" :class="val.isMet ? 'bg-emerald-50/5' : 'bg-red-50/5'">
                          <td class="px-10 py-2.5 text-gray-400 w-1/4">{{ field }}</td>
                          <td class="px-8 py-2.5 text-gray-500 text-[9px]">REQ: {{ val.expected }}</td>
                          <td class="px-8 py-2.5" :class="val.isMet ? 'text-emerald-700' : 'text-red-700'">ACT: {{ val.actual }}</td>
                          <td class="px-8 py-2.5 text-right pr-10">{{ val.isMet ? '✓' : '✕' }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <!-- Professionalism Table -->
              <div v-if="item.label === 'Professionalism'" class="overflow-x-auto border-t border-gray-100">
                <table class="w-full border-collapse text-left text-xs uppercase">
                  <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                    <tr>
                      <th class="px-8 py-3">Quality Attribute</th>
                      <th class="px-8 py-3">Protocol Policy</th>
                      <th class="px-8 py-3">Audit Outcome</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100 font-bold">
                    <tr v-for="row in profRows" :key="row.label" :class="row.isMet ? 'bg-emerald-50/10 text-emerald-800' : 'bg-red-50/10 text-red-800'">
                      <td class="px-8 py-3 text-gray-400">{{ row.label }}</td>
                      <td class="px-8 py-3">{{ row.req }}</td>
                      <td class="px-8 py-3">{{ row.status }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

            </div>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="sticky bottom-0 z-30 bg-gray-50 border-t border-gray-200 p-6 flex items-center justify-between">
         <div class="hidden sm:flex items-center gap-2">
            <i class="ph ph-fingerprint text-gray-400"></i>
            <p class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Assessment Record Hash: #{{ activity?.id }}-{{ (Math.random() * 100000).toFixed(0) }}</p>
         </div>
         <div class="flex gap-3 w-full sm:w-auto">
           <button @click="closeModal" class="flex-1 sm:px-10 py-4 text-[10px] font-bold text-gray-500 bg-white border border-gray-200 hover:bg-gray-100 rounded-xl transition-all uppercase tracking-widest">
             Close Analysis
           </button>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  isLoading: Boolean,
  errorMessage: String,
  activity: Object,
  booking: Object,
  grade: {
    type: [Number, String],
    default: null
  }
});

const emit = defineEmits(['close']);
const closeModal = () => emit('close');

// --- Helper Functions Mirroring instructor_students_score.vue ---

const normalizeTripTypeToCode = (str) => {
    return (str || '').toLowerCase().trim().replace(/[\s-]+/g, '_');
};

const normalizedTripType = computed(() => {
    return normalizeTripTypeToCode(props.activity?.required_trip_type || '');
});

const calculateLevel = (ratio, type) => {
    if (ratio >= 1.0) return { level: 5, status: 'Excellent' };
    if (ratio >= 0.8) return { level: 4, status: 'Very Good' };
    if (ratio >= 0.5) return { level: 3, status: 'Satisfactory' };
    if (ratio >= 0.2) return { level: 2, status: 'Needs Improvement' };
    return { level: 1, status: 'Poor' };
};

const isPassengerSectionMet = (p) => {
    return Object.values(p).every(v => v.isMet);
};

// --- Matching Logic (Advanced) ---

const actualSegments = computed(() => {
  if (!props.booking?.details) return [];
  const segs = [];
  const seen = new Set();
  const sorted = [...props.booking.details].sort((a,b) => (a.schedule?.departure_time || '') < (b.schedule?.departure_time || '') ? -1 : 1);
  sorted.forEach(d => {
    if (!d.schedule) return;
    const key = `${d.schedule.origin}-${d.schedule.destination}-${d.schedule.departure_time}`;
    if (!seen.has(key)) {
      seen.add(key);
      segs.push({
        origin: d.schedule.origin,
        destination: d.schedule.destination,
        date: d.schedule.departure_time ? d.schedule.departure_time.split('T')[0] : 'N/A'
      });
    }
  });
  return segs;
});

const actualClass = computed(() => {
    if (!props.booking?.details?.length) return 'N/A';
    return props.booking.details[0].seat_class_name || 'N/A';
});

const actualPaxTypes = computed(() => {
    const types = { adult: 0, child: 0, infant: 0 };
    props.booking?.details?.forEach(detail => {
        const type = (detail.passenger_type || 'adult').toLowerCase();
        if (type === 'child') types.child++;
        else if (type === 'infant') types.infant++;
        else types.adult++;
    });
    return types;
});

const matches = computed(() => {
  if (!props.activity || !props.booking) return {};
  
  const m = {
    trip_type: props.activity.required_trip_type?.toLowerCase() === props.booking.trip_type?.toLowerCase(),
    origin: props.activity.required_origin?.toLowerCase() === actualSegments.value[0]?.origin?.toLowerCase(),
    destination: props.activity.required_destination?.toLowerCase() === (normalizedTripType.value === 'round_trip' ? actualSegments.value[0]?.destination?.toLowerCase() : actualSegments.value[actualSegments.value.length - 1]?.destination?.toLowerCase()),
    departure_date: !(props.activity.required_departure_date) || props.activity.required_departure_date === actualSegments.value[0]?.date,
    travel_class: (props.activity.required_travel_class || 'Economy').toLowerCase() === actualClass.value?.toLowerCase(),
    pax_types: actualPaxTypes.value.adult === props.activity.required_passengers && actualPaxTypes.value.child === (props.activity.required_children || 0) && actualPaxTypes.value.infant === (props.activity.required_infants || 0),
    passenger_details: [],
    segments: []
  };

  if (props.activity.passengers) {
    props.activity.passengers.forEach((expected, idx) => {
      const actual = props.booking.details?.find(d => d.passenger?.first_name?.toLowerCase() === expected.first_name?.toLowerCase())?.passenger || props.booking.details?.[idx]?.passenger;
      const detailMatch = {
        name: { expected: `${expected.first_name} ${expected.last_name}`, actual: actual ? `${actual.first_name} ${actual.last_name}` : 'MISSING', isMet: actual && actual.first_name?.toLowerCase() === expected.first_name?.toLowerCase() },
        gender: { expected: expected.gender?.toUpperCase(), actual: (actual?.title || actual?.gender || 'N/A').toUpperCase(), isMet: (actual?.title || actual?.gender || '').toLowerCase().includes(expected.gender?.toLowerCase() || '') },
        dob: { expected: expected.date_of_birth, actual: actual?.date_of_birth || 'MISSING', isMet: actual?.date_of_birth === expected.date_of_birth },
        nationality: { expected: expected.nationality, actual: actual?.nationality || 'MISSING', isMet: actual?.nationality?.toLowerCase() === expected.nationality?.toLowerCase() },
        passport: { expected: expected.passport_number || 'N/A', actual: actual?.passport_number || 'N/A', isMet: (actual?.passport_number || '').trim() === (expected.passport_number || '').trim() }
      };
      m.passenger_details.push(detailMatch);
    });
  }

  return m;
});

// --- Final Sections for UI Tables ---

const routingAuditRows = computed(() => {
    const list = [];
    const m = matches.value;
    list.push({ label: 'Trip Type', requirement: props.activity.required_trip_type, work: props.booking?.trip_type || 'N/A', isMet: m.trip_type });
    list.push({ label: 'Origin', requirement: props.activity.required_origin, work: actualSegments.value[0]?.origin || 'MISSING', isMet: m.origin });
    list.push({ label: 'Destination', requirement: props.activity.required_destination, work: (normalizedTripType.value === 'round_trip' ? actualSegments.value[0]?.destination : actualSegments.value[actualSegments.value.length - 1]?.destination) || 'MISSING', isMet: m.destination });
    list.push({ label: 'Date', requirement: props.activity.required_departure_date || 'ANY', work: actualSegments.value[0]?.date || 'MISSING', isMet: m.departure_date });
    return list;
});

const techRows = computed(() => {
    const m = matches.value;
    return [
        { label: 'Cabin Class', requirement: props.activity.required_travel_class || 'Economy', work: actualClass.value, isMet: m.travel_class },
        { label: 'Passenger Manifest', requirement: `${props.activity.required_passengers} Adult Enrollment`, work: `${actualPaxTypes.value.adult} Registered`, isMet: m.pax_types }
    ];
});

const profRows = computed(() => {
    const m = matches.value;
    return [
        { label: 'Route Integrity', req: 'Strict origin/destination matching', status: (m.origin && m.destination) ? 'PROFESSIONAL' : 'LOGIC ERROR', isMet: m.origin && m.destination },
        { label: 'Budget Compliance', req: `${props.activity.required_travel_class || 'Standard'} Policy`, status: m.travel_class ? 'COMPLIANT' : 'VIOLATION', isMet: m.travel_class },
        { label: 'Data Governance', req: 'Accurate Passenger Profile Sync', status: m.passenger_details.every(p => p.name.isMet) ? 'CLEAN RECORD' : 'DATA DISCREPANCY', isMet: m.passenger_details.every(p => p.name.isMet) }
    ];
});

// --- Performance Rubrics (5 Items) ---

const rubricBreakdown = computed(() => {
    if (!props.activity || !props.booking) return [];
    const m = matches.value;
    const isPassport = props.activity.title?.toLowerCase().includes('passport');

    // Accuracy
    const accuracyMet = routingAuditRows.value.filter(r => r.isMet).length;
    const accuracyRatio = accuracyMet / routingAuditRows.value.length;
    const acc = calculateLevel(accuracyRatio);
    
    // Tech Skill
    const techMet = techRows.value.filter(r => r.isMet).length;
    const techRatio = techMet / techRows.value.length;
    const tech = calculateLevel(techRatio);

    // Organization
    const orgMet = m.passenger_details.filter(p => isPassengerSectionMet(p)).length;
    const orgRatio = m.passenger_details.length > 0 ? orgMet / m.passenger_details.length : 1;
    const org = calculateLevel(orgRatio);

    // Professionalism
    const profMet = profRows.value.filter(r => r.isMet).length;
    const profRatio = profMet / profRows.value.length;
    const prof = calculateLevel(profRatio);

    return [
        { label: isPassport ? 'Accuracy of Process' : 'Accuracy of Booking', level: acc.level, status: acc.status, description: acc.level >= 4 ? 'Precision-perfect routing and protocol alignment.' : 'Minor deviations detected in routing parameters.', criteria: routingAuditRows.value.map(r => ({ label: r.label, isMet: r.isMet })) },
        { label: 'Technical Skill', level: techMet === techRows.value.length ? 5 : (techMet > 0 ? 3 : 1), status: tech.status, description: 'Mastery of GDS configuration and seat selection protocols.', criteria: techRows.value.map(r => ({ label: r.label, isMet: r.isMet })) },
        { label: isPassport ? 'Organization' : 'Organization of Steps', level: org.level, status: org.status, description: 'Sequence and documentation of passenger records.', criteria: m.passenger_details.map((p, i) => ({ label: `Pax ${i+1} Sync`, isMet: isPassengerSectionMet(p) })) },
        { label: 'Completeness', level: (m.pax_types && m.origin && m.destination) ? 5 : 3, status: (m.pax_types && m.origin && m.destination) ? 'Excellent' : 'Incomplete', description: 'Comprehensive coverage of all itinerary requirements.', criteria: [{ label: 'Pax Counts', isMet: m.pax_types }, { label: 'Route Segments', isMet: m.origin && m.destination }] },
        { label: 'Professionalism', level: prof.level, status: prof.status, description: 'Alignment with professional airline operation standards.', criteria: profRows.value.map(r => ({ label: r.label, isMet: r.isMet })) }
    ];
});

const calculatedScore = computed(() => {
    if (props.grade !== null) return parseFloat(props.grade);
    const sum = rubricBreakdown.value.reduce((acc, r) => acc + (r.level / 5), 0);
    return (sum / 5) * (props.activity?.total_points || 100);
});

</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
.animate-in {
  animation: modalEnter 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes modalEnter {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
</style>


