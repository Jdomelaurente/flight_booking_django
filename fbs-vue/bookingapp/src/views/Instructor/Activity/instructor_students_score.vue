<template>
  <div class="p-8 max-w-7xl mx-auto space-y-8">
          <!-- Navigation Back Link -->
          <div class="mb-6">
            <button @click="goBack" class="text-sm font-semibold text-gray-500 hover:text-black transition-all flex items-center gap-2">
              ← Back to Submissions
            </button>
          </div>

          <div v-if="loading" class="flex flex-col items-center justify-center py-20">
            <div class="w-12 h-1 bg-gray-200 rounded-full overflow-hidden mb-4">
              <div class="h-full bg-blue-500 w-1/3 animate-[loading_1s_infinite_linear]"></div>
            </div>
            <p class="text-xs font-bold text-gray-500 uppercase tracking-widest">Generating Assessment Analysis...</p>
          </div>

          <div v-else class="space-y-8">

      

      <!-- Top Card: Activity Summary & Score -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-10 flex flex-col lg:flex-row gap-12">
        <!-- Left: Activity Info & Score -->
        <div class="flex-1 space-y-8">
          <div>
            <h1 class="text-4xl font-light mb-2 tracking-wide text-gray-900">{{ activity?.title || 'Assessment Title' }}</h1>
            <p class="text-gray-500 font-medium text-lg">Section: {{ activity?.section?.name || activity?.section_code || 'N/A' }} | {{ activity?.course_code || 'CS-101' }} - {{ activity?.block || 'Block A' }}</p>
            <p class="text-gray-400 text-sm mt-1">Due: {{ formatDueDate(activity?.due_date) }}</p>
            
            <div class="flex flex-wrap gap-2 mt-4">
              <span class="px-3 py-1 bg-pink-100 text-pink-600 text-[10px] font-black rounded-full uppercase tracking-widest border border-pink-200">
                Student: {{ student?.first_name }} {{ student?.last_name }} ({{ student?.student_number }})
              </span>
              <span v-if="actualRoute" class="px-3 py-1 bg-blue-100 text-blue-600 text-[10px] font-black rounded-full uppercase tracking-widest border border-blue-200">
                Route: {{ actualRoute }}
              </span>
              <span class="px-3 py-1 bg-green-100 text-green-600 text-[10px] font-black rounded-full uppercase tracking-widest border border-green-200">Assessment Active</span>
            </div>
          </div>

          <div class="space-y-4">
            <p class="text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Final Assessment Score:</p>
            <div class="bg-[#D1FAE5] rounded-lg p-10 flex items-center justify-center border border-[#A7F3D0]">
              <span class="text-6xl font-black tracking-tighter text-emerald-900">
                {{ calculatePercentage(calculatedScore, activity?.total_points || 100) }}%
              </span>
            </div>
          </div>

          <!-- NEW: Digital Proctor Recommendation -->
          <div class="bg-blue-50 border border-blue-100 rounded-xl p-6 space-y-3">
             <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center text-white shadow-sm">
                   <i class="ph ph-brain text-lg"></i>
                </div>
                <h4 class="text-[10px] font-black text-blue-600 uppercase tracking-widest">Digital Proctor Recommendation</h4>
             </div>
             <p v-if="!booking" class="text-xs text-blue-800 font-bold leading-relaxed">
                The student failed to complete the booking within the allocated time. We recommend a score of 0% and assigning a remedial activity to practice terminal speed.
             </p>
             <p v-else-if="calculatePercentage(calculatedScore, activity?.total_points || 100) >= 90" class="text-xs text-blue-800 font-bold leading-relaxed">
                Outstanding accuracy. The student has mastered the GDS workflow for this itinerary. No intervention needed.
             </p>
             <p v-else-if="calculatePercentage(calculatedScore, activity?.total_points || 100) >= 70" class="text-xs text-blue-800 font-bold leading-relaxed">
                Technically sound, but review the **Passenger Profile** matches. There were slight mismatches in data entry (Names/Passport info) that affected the accuracy rubric.
             </p>
             <p v-else class="text-xs text-blue-800 font-bold leading-relaxed">
                Critical deviations detected in **Routing** or **Cabin Class**. It appears the student struggled with the core instruction set. Professionalism score is weighted down due to non-compliance.
             </p>
          </div>
        </div>

        <!-- Right: Score Breakdown Rubrics -->
        <div class="w-full lg:w-1/2 bg-[#F9FAFB] rounded-xl border border-gray-100 p-8">
          <h2 class="text-xs font-black text-gray-400 uppercase tracking-widest mb-8">Rubric Assessment Breakdown</h2>
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
              <div class="w-full h-2 bg-white rounded-full overflow-hidden flex border border-gray-100">
                <div 
                  class="h-full transition-all duration-1000" 
                  :class="getBarColorForLevel(item.level)"
                  :style="{ width: (item.level / 5 * 100) + '%' }"
                ></div>
              </div>
              <p class="text-[10px] text-gray-500 italic">{{ item.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Rubric Detail & Verification Sections -->
      <div v-for="item in rubricBreakdown" :key="item.label" class="space-y-4">
        <!-- Rubric Header Card -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="px-6 py-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-xs font-black text-gray-900 uppercase tracking-widest">{{ item.label }}</h3>
            <span class="px-2 py-1 bg-emerald-100 text-emerald-700 text-[9px] font-black rounded uppercase">Level {{ item.level }} - {{ item.status }}</span>
          </div>
          <div class="p-6 border-b border-gray-100">
            <p class="text-sm text-gray-700 font-medium leading-relaxed">{{ item.description }}</p>
            <div class="flex flex-wrap gap-2 mt-4">
              <span v-for="tag in item.criteria" :key="tag.label" 
                class="px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-wider"
                :class="tag.isMet ? 'bg-green-50 text-green-600 border border-green-100' : 'bg-red-50 text-red-600 border border-red-100'"
              >
                {{ tag.label }}
              </span>
            </div>
          </div>

          <!-- Nested Verification Tables for this Rubric -->
          
          <!-- Case 1: Accuracy of Booking / Process -->
          <div v-if="item.label.includes('Accuracy')" class="overflow-x-auto bg-white">
            <table class="w-full border-collapse text-left text-xs uppercase">
              <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                 <tr>
                   <th class="px-8 py-3">Selection Category</th>
                   <th class="px-8 py-3">Instruction (Required)</th>
                   <th class="px-8 py-3">Student Choice (Actual)</th>
                   <th class="px-8 py-3 pr-10 text-right">Status</th>
                 </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 font-bold">
                <tr v-if="comparisonRows.find(r => r.label === 'Trip Type')" 
                  class="transition-colors"
                  :class="comparisonRows.find(r => r.label === 'Trip Type').isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'"
                >
                   <td class="px-8 py-3 text-gray-400">{{ comparisonRows.find(r => r.label === 'Trip Type').label }}</td>
                  <td class="px-8 py-3 text-gray-800">{{ comparisonRows.find(r => r.label === 'Trip Type').requirement }}</td>
                  <td class="px-8 py-3" :class="comparisonRows.find(r => r.label === 'Trip Type').isMet ? 'text-emerald-700' : 'text-red-700'">
                    {{ comparisonRows.find(r => r.label === 'Trip Type').work }}
                  </td>
                  <td class="px-8 py-3 pr-10 text-right">{{ comparisonRows.find(r => r.label === 'Trip Type').isMet ? '✓' : '✕' }}</td>
                </tr>
              </tbody>
            </table>

            <!-- One-Way Verification Table Inline -->
            <div v-if="normalizedTripType === 'one_way'" class="p-0 border-t border-gray-100">
               <table class="w-full border-collapse text-left text-xs uppercase">
                 <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                   <tr>
                     <th class="px-8 py-3">Routing Parameter</th>
                     <th class="px-8 py-3">Instruction (Required)</th>
                     <th class="px-8 py-3">Student Choice (Actual)</th>
                     <th class="px-8 py-3 pr-10 text-right">Status</th>
                   </tr>
                 </thead>
                 <tbody class="divide-y divide-gray-100 font-bold">
                   <tr :class="matches.origin ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Origin City</td>
                     <td class="px-8 py-3 text-gray-800">{{ activity.required_origin }}</td>
                     <td class="px-8 py-3" :class="matches.origin ? 'text-emerald-700' : 'text-red-700'">{{ actualOrigin }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.origin ? '✓' : '✕' }}</td>
                   </tr>
                   <tr :class="matches.destination ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Destination City</td>
                     <td class="px-8 py-3 text-gray-800">{{ activity.required_destination }}</td>
                     <td class="px-8 py-3" :class="matches.destination ? 'text-emerald-700' : 'text-red-700'">{{ actualDestination }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.destination ? '✓' : '✕' }}</td>
                   </tr>
                   <tr :class="matches.departure_date ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Departure Date</td>
                     <td class="px-8 py-3 text-gray-800">{{ activity.required_departure_date || 'ANY' }}</td>
                     <td class="px-8 py-3" :class="matches.departure_date ? 'text-emerald-700' : 'text-red-700'">{{ actualDepartureDate }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.departure_date ? '✓' : '✕' }}</td>
                   </tr>
                   <tr :class="matches.travel_class ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Travel Class</td>
                     <td class="px-8 py-3 text-gray-800">{{ formatTravelClass(activity.required_travel_class) }}</td>
                     <td class="px-8 py-3" :class="matches.travel_class ? 'text-emerald-700' : 'text-red-700'">{{ actualClass }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.travel_class ? '✓' : '✕' }}</td>
                   </tr>
                   <tr v-if="activity.required_seat_class" :class="matches.fare_type ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Ticket Bundle</td>
                     <td class="px-8 py-3 text-gray-800">{{ activity.required_seat_class }}</td>
                     <td class="px-8 py-3" :class="matches.fare_type ? 'text-emerald-700' : 'text-red-700'">{{ actualFareType }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.fare_type ? '✓' : '✕' }}</td>
                   </tr>
                 </tbody>
               </table>
            </div>

            <!-- Round-Trip Verification Table Inline -->
            <div v-if="normalizedTripType === 'round_trip'" class="p-0 border-t border-gray-100">
               <table class="w-full border-collapse text-left text-xs uppercase">
                 <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                   <tr>
                     <th class="px-8 py-3">Leg / Parameter</th>
                     <th class="px-8 py-3">Instruction (Required)</th>
                     <th class="px-8 py-3">Student Choice (Actual)</th>
                     <th class="px-8 py-3 pr-10 text-right">Status</th>
                   </tr>
                 </thead>
                 <tbody class="divide-y divide-gray-100 font-bold">
                   <tr :class="matches.origin && matches.destination ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Outbound Route</td>
                     <td class="px-8 py-3 text-gray-800">{{ activity.required_origin }} → {{ activity.required_destination }}</td>
                     <td class="px-8 py-3" :class="matches.origin && matches.destination ? 'text-emerald-700' : 'text-red-700'">{{ actualOrigin }} → {{ actualDestination }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.origin && matches.destination ? '✓' : '✕' }}</td>
                   </tr>
                   <tr :class="matches.return_origin && matches.return_destination ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Return Route</td>
                     <td class="px-8 py-3 text-gray-800">{{ activity.required_destination }} → {{ activity.required_origin }}</td>
                     <td class="px-8 py-3" :class="matches.return_origin && matches.return_destination ? 'text-emerald-700' : 'text-red-700'">{{ actualReturnOrigin }} → {{ actualReturnDestination }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.return_origin && matches.return_destination ? '✓' : '✕' }}</td>
                   </tr>
                   <tr :class="matches.departure_date ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Outbound Date</td>
                     <td class="px-8 py-3 text-gray-800">{{ activity.required_departure_date || 'ANY' }}</td>
                     <td class="px-8 py-3" :class="matches.departure_date ? 'text-emerald-700' : 'text-red-700'">{{ actualDepartureDate }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.departure_date ? '✓' : '✕' }}</td>
                   </tr>
                   <tr :class="matches.return_date ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Return Date</td>
                     <td class="px-8 py-3 text-gray-800">{{ activity.required_return_date || 'ANY' }}</td>
                     <td class="px-8 py-3" :class="matches.return_date ? 'text-emerald-700' : 'text-red-700'">{{ actualReturnDate }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.return_date ? '✓' : '✕' }}</td>
                   </tr>
                   <tr :class="matches.travel_class ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Travel Class</td>
                     <td class="px-8 py-3 text-gray-800">{{ formatTravelClass(activity.required_travel_class) }}</td>
                     <td class="px-8 py-3" :class="matches.travel_class ? 'text-emerald-700' : 'text-red-700'">{{ actualClass }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.travel_class ? '✓' : '✕' }}</td>
                   </tr>
                   <tr v-if="activity.required_seat_class" :class="matches.fare_type ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Ticket Bundle</td>
                     <td class="px-8 py-3 text-gray-800">{{ activity.required_seat_class }}</td>
                     <td class="px-8 py-3" :class="matches.fare_type ? 'text-emerald-700' : 'text-red-700'">{{ actualFareType }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.fare_type ? '✓' : '✕' }}</td>
                   </tr>
                 </tbody>
               </table>
            </div>

            <!-- Multi-City Table Inline -->
            <div v-if="normalizedTripType === 'multi_city'" class="p-0 border-t border-gray-100">
               <table class="w-full border-collapse text-left text-xs uppercase">
                 <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                   <tr>
                     <th class="px-8 py-3">Segment</th>
                     <th class="px-8 py-3">Instruction (Required)</th>
                     <th class="px-8 py-3">Student Choice (Actual)</th>
                     <th class="px-8 py-3 pr-10 text-right">Status</th>
                   </tr>
                 </thead>
                 <tbody class="divide-y divide-gray-100 font-bold">
                   <tr v-for="(seg, idx) in activity.segments" :key="idx"
                     :class="matches.segments?.[idx]?.origin && matches.segments?.[idx]?.destination ? 'bg-emerald-50/10' : 'bg-red-50/10'"
                   >
                     <td class="px-8 py-3 text-gray-400">Leg {{ idx + 1 }}</td>
                     <td class="px-8 py-3 text-gray-800">{{ seg.origin }} → {{ seg.destination }}</td>
                     <td class="px-8 py-3" :class="matches.segments?.[idx]?.origin && matches.segments?.[idx]?.destination ? 'text-emerald-700' : 'text-red-700'">
                       <span v-if="matches.segments?.[idx]?.actualData">{{ matches.segments[idx].actualData.origin }} → {{ matches.segments[idx].actualData.destination }}</span>
                       <span v-else>NOT BOOKED</span>
                     </td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.segments?.[idx]?.origin && matches.segments?.[idx]?.destination ? '✓' : '✕' }}</td>
                   </tr>
                   <tr v-for="(seg, idx) in activity.segments" :key="'date-' + idx"
                     :class="matches.segments?.[idx]?.departure_date ? 'bg-emerald-50/10' : 'bg-red-50/10'"
                   >
                     <td class="px-8 py-3 text-gray-400">Leg {{ idx + 1 }} Date</td>
                     <td class="px-8 py-3 text-gray-800">{{ seg.departure_date || 'ANY' }}</td>
                     <td class="px-8 py-3" :class="matches.segments?.[idx]?.departure_date ? 'text-emerald-700' : 'text-red-700'">
                       <span v-if="matches.segments?.[idx]?.actualData">{{ matches.segments[idx].actualData.departure_date }}</span>
                       <span v-else>NOT BOOKED</span>
                     </td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.segments?.[idx]?.departure_date ? '✓' : '✕' }}</td>
                   </tr>
                   <tr v-for="(seg, idx) in activity.segments" :key="'class-' + idx"
                     :class="matches.segments?.[idx]?.travel_class ? 'bg-emerald-50/10' : 'bg-red-50/10'"
                   >
                     <td class="px-8 py-3 text-gray-400">Leg {{ idx + 1 }} Travel Class</td>
                     <td class="px-8 py-3 text-gray-800">{{ formatTravelClass(activity.required_travel_class) }}</td>
                     <td class="px-8 py-3" :class="matches.segments?.[idx]?.travel_class ? 'text-emerald-700' : 'text-red-700'">
                       <span v-if="matches.segments?.[idx]?.actualData?.seat_class_name">{{ formatTravelClass(matches.segments[idx].actualData.seat_class_name) }}</span>
                       <span v-else>NOT SPECIFIED</span>
                     </td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.segments?.[idx]?.travel_class ? '✓' : '✕' }}</td>
                   </tr>
                   <tr v-if="activity.required_seat_class" :class="matches.fare_type ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                     <td class="px-8 py-3 text-gray-400">Ticket Bundle</td>
                     <td class="px-8 py-3 text-gray-800">{{ activity.required_seat_class }}</td>
                     <td class="px-8 py-3" :class="matches.fare_type ? 'text-emerald-700' : 'text-red-700'">{{ actualFareType }}</td>
                     <td class="px-8 py-3 pr-10 text-right">{{ matches.fare_type ? '✓' : '✕' }}</td>
                   </tr>
                 </tbody>
               </table>
            </div>
          </div>

          <!-- Case 2: Technical Skill -->
          <div v-if="item.label === 'Technical Skill'" class="overflow-x-auto border-t border-gray-100">
            <table class="w-full border-collapse text-left text-xs uppercase">
              <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                 <tr>
                   <th class="px-8 py-3">Technical Parameter</th>
                   <th class="px-8 py-3">Instruction (Required)</th>
                   <th class="px-8 py-3">Student Choice (Actual)</th>
                   <th class="px-8 py-3 pr-10 text-right">Status</th>
                 </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 font-bold">
                <tr v-for="row in comparisonRows.filter(r => ['Travel Class', 'Infant Seating'].includes(r.label))" 
                  :key="row.label"
                  :class="row.isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'"
                >
                  <td class="px-8 py-3 text-gray-400">{{ row.label === 'Infant Seating' ? 'Infant Logic' : row.label }}</td>
                  <td class="px-8 py-3 text-gray-800">{{ row.requirement }}</td>
                  <td class="px-8 py-3" :class="row.isMet ? 'text-emerald-700' : 'text-red-700'">{{ row.work !== 'N/A' ? row.work : 'NOT SPECIFIED' }}</td>
                  <td class="px-8 py-3 pr-10 text-right">{{ row.isMet ? '✓' : '✕' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="item.label.includes('Organization')" class="border-t border-gray-100">
            <div v-for="(p, idx) in matches.passenger_details" :key="idx" class="border-b last:border-0 border-gray-100 overflow-hidden">
              <!-- Passenger Header -->
              <div class="px-8 py-4 bg-gray-50/30 flex justify-between items-center"
                :class="isPassengerPerfect(p) ? 'bg-emerald-50/30' : 'bg-red-50/30'"
              >
                <span class="text-xs font-black text-gray-500 uppercase tracking-widest">Passenger {{ idx + 1 }}: {{ p.name?.expected }}</span>
                <span class="text-[10px] font-black uppercase px-2 py-0.5 rounded"
                  :class="isPassengerPerfect(p) ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600'"
                >
                  {{ isPassengerPerfect(p) ? 'DATA ACCURATE' : 'DATA ERRORS' }}
                </span>
              </div>

              <!-- Detailed Passenger Verification Table -->
              <div class="overflow-x-auto">
                <table class="w-full border-collapse text-left text-xs uppercase">
                  <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                    <tr>
                      <th class="px-8 py-3">Passenger Attribute</th>
                      <th class="px-8 py-3">Instruction (Required)</th>
                      <th class="px-8 py-3">Student Choice (Actual)</th>
                      <th class="px-8 py-3 pr-10 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100 font-bold">
                    <!-- Passenger Type Check -->
                    <tr :class="p.passengerType?.isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Passenger Type</td>
                      <td class="px-8 py-3 text-gray-800">{{ p.passengerType?.expected }}</td>
                      <td class="px-8 py-3" :class="p.passengerType?.isMet ? 'text-emerald-700' : 'text-red-700'">{{ p.passengerType?.actual }}</td>
                      <td class="px-8 py-3 pr-10 text-right">{{ p.passengerType?.isMet ? '✓' : '✕' }}</td>
                    </tr>
                    <!-- Name Check -->
                    <tr :class="p.name?.isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Full Name</td>
                      <td class="px-8 py-3 text-gray-800">{{ p.name?.expected }}</td>
                      <td class="px-8 py-3" :class="p.name?.isMet ? 'text-emerald-700' : 'text-red-700'">{{ p.name?.actual }}</td>
                      <td class="px-8 py-3 pr-10 text-right">{{ p.name?.isMet ? '✓' : '✕' }}</td>
                    </tr>
                    <!-- Gender Check -->
                    <tr :class="p.gender?.isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Gender/Title</td>
                      <td class="px-8 py-3 text-gray-800">{{ p.gender?.expected }}</td>
                      <td class="px-8 py-3" :class="p.gender?.isMet ? 'text-emerald-700' : 'text-red-700'">{{ p.gender?.actual }}</td>
                      <td class="px-8 py-3 pr-10 text-right">{{ p.gender?.isMet ? '✓' : '✕' }}</td>
                    </tr>
                    <!-- DOB Check -->
                    <tr :class="p.dob?.isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Date of Birth</td>
                      <td class="px-8 py-3 text-gray-800">{{ p.dob?.expected }}</td>
                      <td class="px-8 py-3" :class="p.dob?.isMet ? 'text-emerald-700' : 'text-red-700'">{{ p.dob?.actual }}</td>
                      <td class="px-8 py-3 pr-10 text-right">{{ p.dob?.isMet ? '✓' : '✕' }}</td>
                    </tr>
                    <!-- Nationality Check -->
                    <tr :class="p.nationality?.isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Nationality</td>
                      <td class="px-8 py-3 text-gray-800">{{ p.nationality?.expected }}</td>
                      <td class="px-8 py-3" :class="p.nationality?.isMet ? 'text-emerald-700' : 'text-red-700'">{{ p.nationality?.actual }}</td>
                      <td class="px-8 py-3 pr-10 text-right">{{ p.nationality?.isMet ? '✓' : '✕' }}</td>
                    </tr>
                    <!-- Category Check -->
                    <tr :class="p.category?.isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Category</td>
                      <td class="px-8 py-3 text-gray-800">{{ p.category?.expected }}</td>
                      <td class="px-8 py-3" :class="p.category?.isMet ? 'text-emerald-700' : 'text-red-700'">{{ p.category?.actual }}</td>
                      <td class="px-8 py-3 pr-10 text-right">{{ p.category?.isMet ? '✓' : '✕' }}</td>
                    </tr>
                    <!-- Seating Check -->
                    <tr :class="p.seating?.isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Assigned Seat</td>
                      <td class="px-8 py-3 text-gray-800">{{ p.seating?.expected }}</td>
                      <td class="px-8 py-3" :class="p.seating?.isMet ? 'text-emerald-700' : 'text-red-700'">{{ p.seating?.actual }}</td>
                      <td class="px-8 py-3 pr-10 text-right">{{ p.seating?.isMet ? '✓' : '✕' }}</td>
                    </tr>
                    <!-- Passport Check -->
                    <tr v-if="activity.require_passport" :class="p.passport?.isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Passport Number</td>
                      <td class="px-8 py-3 text-gray-800">{{ p.passport?.expected }}</td>
                      <td class="px-8 py-3" :class="p.passport?.isMet ? 'text-emerald-700' : 'text-red-700'">{{ p.passport?.actual }}</td>
                      <td class="px-8 py-3 pr-10 text-right">{{ p.passport?.isMet ? '✓' : '✕' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Case 4: Completeness -->
          <div v-if="item.label === 'Completeness'" class="overflow-x-auto border-t border-gray-100">
            <table class="w-full border-collapse text-left text-xs uppercase">
              <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                 <tr>
                   <th class="px-8 py-3">Completeness Parameter</th>
                   <th class="px-8 py-3">Instruction (Required)</th>
                   <th class="px-8 py-3">Student Choice (Actual)</th>
                   <th class="px-8 py-3 pr-10 text-right">Status</th>
                 </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 font-bold">
                <tr v-if="comparisonRows.find(r => r.label === 'Passengers')" 
                  class="transition-colors"
                  :class="comparisonRows.find(r => r.label === 'Passengers').isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'"
                >
                  <td class="px-8 py-3 text-gray-400">Total Passengers</td>
                  <td class="px-8 py-3 text-gray-800">{{ comparisonRows.find(r => r.label === 'Passengers').requirement }}</td>
                  <td class="px-8 py-3" :class="comparisonRows.find(r => r.label === 'Passengers').isMet ? 'text-emerald-700' : 'text-red-700'">
                    {{ comparisonRows.find(r => r.label === 'Passengers').work }}
                  </td>
                  <td class="px-8 py-3 pr-10 text-right">{{ comparisonRows.find(r => r.label === 'Passengers').isMet ? '✓' : '✕' }}</td>
                </tr>
              </tbody>
            </table>
            <!-- Add-ons in Completeness -->
            <div v-if="matches.addons?.length" class="border-t border-gray-100">
               <div class="px-8 py-4 bg-gray-50/50 border-b border-gray-100">
                 <h4 class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Service Add-ons & Insurance Verification</h4>
               </div>
               <div class="overflow-x-auto">
                 <table class="w-full border-collapse text-left text-xs uppercase">
                   <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                     <tr>
                       <th class="px-8 py-3">Passenger</th>
                       <th class="px-8 py-3">Requirement (Instruction)</th>
                       <th class="px-8 py-3">Student Choice (Actual)</th>
                       <th class="px-8 py-3 pr-10 text-right">Status</th>
                     </tr>
                   </thead>
                   <tbody class="divide-y divide-gray-100 font-bold">
                     <tr v-for="(addon, aIdx) in matches.addons" :key="aIdx"
                       :class="addon.isMet ? 'bg-emerald-50/10' : 'bg-red-50/10'"
                     >
                       <td class="px-8 py-3 text-gray-400">{{ addon.passengerName }}</td>
                       <td class="px-8 py-3 text-gray-800">{{ addon.requirement }}</td>
                       <td class="px-8 py-3" :class="addon.isMet ? 'text-emerald-700' : 'text-red-700'">{{ addon.actual }}</td>
                       <td class="px-8 py-3 pr-10 text-right">{{ addon.isMet ? '✓' : '✕' }}</td>
                     </tr>
                   </tbody>
                 </table>
               </div>
            </div>
          </div>

          <!-- Case 5: Professionalism -->
          <div v-if="item.label === 'Professionalism'" class="overflow-x-auto border-t border-gray-100">
             <table class="w-full border-collapse text-left text-xs uppercase">
                <thead class="bg-gray-50/20 text-[9px] font-black tracking-widest text-gray-400 border-b border-gray-100">
                  <tr>
                    <th class="px-8 py-3">Professional Attribute</th>
                    <th class="px-8 py-3">Instruction (Required)</th>
                    <th class="px-8 py-3">Student Choice (Actual)</th>
                    <th class="px-8 py-3 pr-10 text-right">Status</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100 font-bold">
                   <tr :class="(normalizedTripType === 'multi_city' ? (matches.segments?.every(s => s.origin && s.destination)) : (matches.origin && matches.destination)) ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Flight Route Integrity</td>
                      <td class="px-8 py-3 text-gray-800 text-[10px]">{{ requiredRoute }}</td>
                      <td class="px-8 py-3" :class="(normalizedTripType === 'multi_city' ? (matches.segments?.every(s => s.origin && s.destination)) : (matches.origin && matches.destination)) ? 'text-emerald-700' : 'text-red-700'">{{ actualRoute || (actualOrigin + ' to ' + actualDestination) }}</td>
                      <td class="px-8 py-3 pr-10 text-right">
                         <span :class="(normalizedTripType === 'multi_city' ? (matches.segments?.every(s => s.origin && s.destination)) : (matches.origin && matches.destination)) ? 'text-emerald-600' : 'text-red-600'">
                           {{ (normalizedTripType === 'multi_city' ? (matches.segments?.every(s => s.origin && s.destination)) : (matches.origin && matches.destination)) ? 'PROFESSIONAL' : 'LOGIC ERROR' }}
                         </span>
                      </td>
                   </tr>
                    <tr :class="matches.travel_class ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Budget Compliance (Class)</td>
                      <td class="px-8 py-3 text-gray-800 text-[10px]">{{ formatTravelClass(activity.required_travel_class) }} Policy</td>
                      <td class="px-8 py-3" :class="matches.travel_class ? 'text-emerald-700' : 'text-red-700'">{{ actualClass !== 'NOT SPECIFIED' && actualClass !== 'N/A' ? actualClass : 'NOT SPECIFIED' }}</td>
                      <td class="px-8 py-3 pr-10 text-right">
                         <span :class="matches.travel_class ? 'text-emerald-600' : 'text-red-600'">{{ matches.travel_class ? 'COMPLIANT' : 'VIOLATION' }}</span>
                      </td>
                   </tr>
                   <tr :class="isPassengerPerfect(matches.passenger_details?.[0] || {}) ? 'bg-emerald-50/10' : 'bg-red-50/10'">
                      <td class="px-8 py-3 text-gray-400">Data Integrity</td>
                      <td class="px-8 py-3 text-gray-800 text-[10px]">Proper Passenger Documentation</td>
                      <td class="px-8 py-3" :class="isPassengerPerfect(matches.passenger_details?.[0] || {}) ? 'text-emerald-700' : 'text-red-700'">Doc Verification</td>
                      <td class="px-8 py-3 pr-10 text-right">
                         <span :class="isPassengerPerfect(matches.passenger_details?.[0] || {}) ? 'text-emerald-600' : 'text-red-600'">{{ isPassengerPerfect(matches.passenger_details?.[0] || {}) ? 'CLEAN RECORD' : 'DATA ERRORS' }}</span>
                      </td>
                   </tr>
                </tbody>
             </table>
             <div class="px-8 py-4 bg-emerald-50/20 text-[10px] text-emerald-800 font-bold uppercase tracking-widest border-t border-gray-100">
                Instruction Alignment: Verified
             </div>
          </div>
        </div>
      </div>


    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { activityDetailsService } from '@/services/instructor/activityDetailsService';
import { bookingService } from '@/services/booking/bookingService';
import { useNotificationStore } from '@/stores/notification';
import { useUserStore } from '@/stores/user';
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService';
import { calculateLevel, calculatePercentage } from '@/utils/gradingLogic';
import CTHM from '@/assets/image/cthm-logos.png';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const sidebarOpen = ref(false);
const sections = ref([]);

// Normalize a trip type string to a canonical raw code form (e.g. "One Way" -> "one_way", "Round Trip" -> "round_trip")
const normalizeTripTypeToCode = (str) => {
    return (str || '').toLowerCase().trim().replace(/[\s-]+/g, '_');
};

const normalizedTripType = computed(() => {
    return normalizeTripTypeToCode(activity.value?.required_trip_type || '');
});
const notificationStore = useNotificationStore();

const activityId = route.params.activityId;
const studentId = route.params.studentId;

const loading = ref(true);
const error = ref(null);
const activity = ref(null);
const booking = ref(null);
const student = ref(null);
const storedGrade = ref(null);
const backendAnalysis = ref(null);
const assignedSeats = ref([]);

const fetchData = async () => {
    loading.value = true;
    error.value = null;
    try {
        const dashData = await instructorDashboardService.getDashboard().catch(() => ({ sections: [] }));
        sections.value = dashData.sections || [];

        const actData = await activityDetailsService.getActivity(activityId);
        activity.value = actData.activity || actData;

        const subData = await activityDetailsService.getSubmissions(activityId);
        const submission = subData.submissions.find(s => s.student_id == studentId);
        
        if (!submission) throw new Error("Submission not found.");
        
        student.value = { first_name: submission.first_name, last_name: submission.last_name, student_number: submission.student_number };
        storedGrade.value = submission.grade;
        backendAnalysis.value = submission.analysis;
        assignedSeats.value = submission.assigned_seats || [];

        if (submission.booking) {
            const bookingRes = await bookingService.getBookingDetails(submission.booking.id);
            if (bookingRes.success) {
                booking.value = bookingRes.booking;
            } else {
                throw new Error("Failed to load booking details.");
            }
        } else {
            console.log("No booking data available for this student (possibly timed out)");
            booking.value = null; // Correctly handle timeout cases
        }
        
        // Wait for computed properties to update based on new data
        await new Promise(resolve => setTimeout(resolve, 300));

        // Auto-save the calculated grade directly to the backend
        const sumOfRatios = rubricBreakdown.value.reduce((acc, r) => acc + r.ratio, 0);
        const totalPoints = parseFloat(activity.value?.total_points || 100);
        const latestGrade = Math.round(sumOfRatios * (totalPoints / 5));

        // Format the breakdown match exactly what the backend expects
        const breakdownPayload = rubricBreakdown.value.map(r => ({
            label: r.label,
            level: r.level,
            ratio: r.ratio,
            status: r.status,
            description: r.description
        }));

        await activityDetailsService.saveGrade(activityId, studentId, {
            grade: latestGrade,
            feedback: "Auto-calculated based on rubric.",
            rubric_breakdown: breakdownPayload
        });

    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
};

// --- Trip-Type Specific Grading Functions ---

const calculateOneWayRoutingScore = (totalPoints, m) => {
    const routingMax = totalPoints * 0.25;
    let score = routingMax;
    // Penalty logic: 80% off if route doesn't match, 50% off if date doesn't match
    if (!m.origin || !m.destination) score *= 0.2;
    if (!m.departure_date) score *= 0.5;
    return Math.max(0, score);
};

const calculateRoundTripRoutingScore = (totalPoints, m) => {
    const routingMax = totalPoints * 0.25;
    const outboundMax = totalPoints * 0.125;
    const returnMax = totalPoints * 0.125;
    
    let outboundScore = outboundMax;
    if (!m.origin || !m.destination) outboundScore *= 0.2;
    if (!m.departure_date) outboundScore *= 0.5;
    
    let returnScore = returnMax;
    if (!m.return_origin || !m.return_destination) returnScore *= 0.2;
    if (!m.return_date) returnScore *= 0.5;
    
    return Math.max(0, outboundScore + returnScore);
};

const calculateMultiCityRoutingScore = (totalPoints, m) => {
    const routingMax = totalPoints * 0.25;
    if (!m.segments || m.segments.length === 0) return 0;
    
    const correctSegs = m.segments.filter(s => s.origin && s.destination && s.departure_date).length;
    return routingMax * (correctSegs / m.segments.length);
};

const rubricBreakdown = computed(() => {
    if (!activity.value) return [];
    
    const isPassport = activity.value.title?.toLowerCase().includes('passport');

    if (!booking.value) {
        // Correctly formatted fallback for students with no data (timeout cases)
        return [
            { 
                label: isPassport ? 'Accuracy of Process' : 'Accuracy of Booking', 
                level: 1, 
                ratio: 0, 
                status: 'Poor', 
                description: 'No booking was recorded before the time expired.',
                criteria: [{ label: 'Booking Recorded', isMet: false }, { label: 'Route Match', isMet: false }]
            },
            { 
                label: 'Technical Skill', 
                level: 1, 
                ratio: 0, 
                status: 'Poor', 
                description: 'System entries could not be evaluated due to inactivity.',
                criteria: [{ label: 'GDS Commands', isMet: false }, { label: 'Class Selection', isMet: false }]
            },
            { 
                label: isPassport ? 'Organization' : 'Organization of Steps', 
                level: 1, 
                ratio: 0, 
                status: 'Poor', 
                description: 'No workflow was observed.',
                criteria: [{ label: 'Passenger Data', isMet: false }, { label: 'Pnr Sequence', isMet: false }]
            },
            { 
                label: 'Completeness', 
                level: 1, 
                ratio: 0, 
                status: 'Poor', 
                description: 'Activity was not finished before the deadline.',
                criteria: [{ label: 'All Pax Booked', isMet: false }, { label: 'Add-ons Added', isMet: false }]
            },
            { 
                label: 'Professionalism', 
                level: 1, 
                ratio: 0, 
                status: 'Poor', 
                description: 'Activity timed out.',
                criteria: [{ label: 'Budget Compliance', isMet: false }, { label: 'Professionalism', isMet: false }]
            }
        ];
    }

    const m = matches.value;
    // Removed duplicate isPassport declaration
    
    // 1. Accuracy of Booking/Process
    const accuracyCriteria = [];
    accuracyCriteria.push({ label: 'Trip Type', isMet: m.trip_type });
    
    if (normalizedTripType.value === 'one_way') {
        accuracyCriteria.push({ label: 'Origin', isMet: m.origin });
        accuracyCriteria.push({ label: 'Destination', isMet: m.destination });
        accuracyCriteria.push({ label: 'Departure Date', isMet: m.departure_date });
    } else if (normalizedTripType.value === 'round_trip') {
        accuracyCriteria.push({ label: 'Outbound Route', isMet: m.origin && m.destination });
        accuracyCriteria.push({ label: 'Return Route', isMet: m.return_origin && m.return_destination });
        accuracyCriteria.push({ label: 'Outbound Date', isMet: m.departure_date });
        accuracyCriteria.push({ label: 'Return Date', isMet: m.return_date });
    } else if (normalizedTripType.value === 'multi_city') {
        if (m.segments?.length) {
            m.segments.forEach((s, i) => {
                accuracyCriteria.push({ label: `Leg ${i+1} Route`, isMet: s.origin && s.destination });
                accuracyCriteria.push({ label: `Leg ${i+1} Date`, isMet: s.departure_date });
            });
        }
    } else {
        // Fallback
        accuracyCriteria.push({ label: 'Origin', isMet: m.origin });
        accuracyCriteria.push({ label: 'Destination', isMet: m.destination });
        accuracyCriteria.push({ label: 'Dates', isMet: m.departure_date && m.return_date });
    }
    const accuracyMetCount = accuracyCriteria.filter(c => c.isMet).length;
    const accuracyRatio = accuracyMetCount / accuracyCriteria.length;
    const accuracyInfo = calculateLevel(accuracyRatio, 'accuracy');
    const accuracyLevel = accuracyInfo.level;

    const accuracyLabels = {
        5: { status: 'Excellent', desc: isPassport ? 'Correct and complete steps.' : 'Correctly simulates all steps.' },
        4: { status: 'Very Good', desc: 'Minor errors but mostly correct.' },
        3: { status: 'Satisfactory', desc: isPassport ? 'Some steps correct, some missing.' : 'Some correct steps, some missing.' },
        2: { status: 'Needs Improvement', desc: isPassport ? 'Many errors.' : 'Many errors, incomplete.' },
        1: { status: 'Poor', desc: isPassport ? 'No process.' : 'No proper booking.' }
    };

    // 2. Technical Skill
    const techCriteria = [
        { label: 'Travel Class', isMet: m.travel_class },
        { label: 'Fare Type', isMet: m.fare_type },
        { label: 'Category', isMet: (m.passenger_details || []).every(p => p.category?.isMet) },
        { label: 'Passport Info', isMet: (m.passenger_details || []).every(p => p.passport?.isMet) }
    ];
    const techRatio = techCriteria.filter(c => c.isMet).length / techCriteria.length;
    const techInfo = calculateLevel(techRatio, 'tech');
    const techLevel = techInfo.level;

    const techLabels = {
        5: { status: 'Excellent', desc: isPassport ? 'Mastery of system navigation.' : 'Demonstrates mastery of platform.' },
        4: { status: 'Very Good', desc: 'Good skill; minor lapses.' },
        3: { status: 'Satisfactory', desc: isPassport ? 'Basic use, lacks detail.' : 'Basic use, lacks depth.' },
        2: { status: 'Needs Improvement', desc: isPassport ? 'Weak navigation.' : 'Weak handling.' },
        1: { status: 'Poor', desc: 'No skill shown.' }
    };

    // 3. Organization of Steps
    const orgCriteria = (m.passenger_details || []).map(p => ({
        label: `Pax ${p.name?.expected?.split(' ')[0]} Details`,
        // Now includes seating check — missing seat = criteria not fully met
        isMet: p.name?.isMet && p.gender?.isMet && p.dob?.isMet && p.nationality?.isMet && p.seating?.isMet
    }));
    
    // Calculate granular ratio for score — seating is now a scored field
    const orgFields = [];
    (m.passenger_details || []).forEach(p => {
        orgFields.push({ label: 'Name', isMet: p.name?.isMet });
        orgFields.push({ label: 'Gender', isMet: p.gender?.isMet });
        orgFields.push({ label: 'DOB', isMet: p.dob?.isMet });
        orgFields.push({ label: 'Nationality', isMet: p.nationality?.isMet });
        // Seat selection is required — missing seat deducts from the Organization score
        orgFields.push({ label: 'Assigned Seat', isMet: p.seating?.isMet });
    });
    const orgRatio = orgFields.length > 0 ? orgFields.filter(f => f.isMet).length / orgFields.length : 1;
    const orgInfo = calculateLevel(orgRatio, 'org');
    const orgLevel = orgInfo.level;

    const orgLabels = {
        5: { status: 'Excellent', desc: isPassport ? 'Clear, sequential steps.' : 'Clear and logical sequence.' },
        4: { status: 'Very Good', desc: 'Mostly clear.' },
        3: { status: 'Satisfactory', desc: 'Understandable but not smooth.' },
        2: { status: 'Needs Improvement', desc: isPassport ? 'Disorganized.' : 'Confusing sequence.' },
        1: { status: 'Poor', desc: isPassport ? 'Very poor.' : 'No sequence.' }
    };

    // 4. Completeness — each required addon is an individual scored criterion
    const compCriteria = [
        { label: 'Passenger Counts', isMet: m.pax_types },
    ];

    // If the activity has required addons, add each one as an individual criterion
    // This gives partial credit (e.g., 2/3 addons correct = 67% of addon score)
    if ((m.addons || []).length > 0) {
        m.addons.forEach(addon => {
            compCriteria.push({
                label: `Add-on: ${addon.requirement} (${addon.passengerName})`,
                isMet: addon.isMet
            });
        });
    } else {
        // No addons required — mark as always met so it doesn't penalize
        compCriteria.push({ label: 'Add-ons Compliance', isMet: true });
    }

    const compRatio = compCriteria.filter(c => c.isMet).length / compCriteria.length;
    const compInfo = calculateLevel(compRatio, 'comp');
    const compLevel = compInfo.level;

    const compLabels = {
        5: { status: 'Excellent', desc: 'Covers all booking requirements.' },
        4: { status: 'Very Good', desc: 'Covers most requirements.' },
        3: { status: 'Satisfactory', desc: 'Covers some requirements.' },
        2: { status: 'Needs Improvement', desc: 'Few requirements covered.' },
        1: { status: 'Poor', desc: 'None covered.' }
    };

    // 5. Professionalism
    const profCriteria = [
        { 
            label: 'Flight Route Integrity', 
            isMet: normalizedTripType.value === 'multi_city'
                ? (m.segments?.length > 0 && m.segments.every(s => s.origin && s.destination))
                : !!(m.origin && m.destination)
        },
        { label: 'Budget Compliance', isMet: m.travel_class },
        { label: 'Data Integrity', isMet: (m.passenger_details || []).length > 0 && isPassengerPerfect(m.passenger_details[0]) }
    ];
    const profRatio = profCriteria.filter(c => c.isMet).length / profCriteria.length;
    const profInfo = calculateLevel(profRatio, 'prof');
    const profLevel = profInfo.level;

    const profLabels = {
        5: { status: 'Excellent', desc: 'Realistic and practical.' },
        4: { status: 'Very Good', desc: 'Mostly realistic.' },
        3: { status: 'Satisfactory', desc: 'Somewhat usable.' },
        2: { status: 'Needs Improvement', desc: 'Not practical.' },
        1: { status: 'Poor', desc: 'Not professional.' }
    };

    const breakdown = [
        { label: isPassport ? 'Accuracy of Process' : 'Accuracy of Booking', level: accuracyLevel, ratio: accuracyRatio, status: accuracyLabels[accuracyLevel].status, description: accuracyLabels[accuracyLevel].desc, criteria: accuracyCriteria },
        { label: 'Technical Skill', level: techLevel, ratio: techRatio, status: techLabels[techLevel].status, description: techLabels[techLevel].desc, criteria: techCriteria },
        { label: isPassport ? 'Organization' : 'Organization of Steps', level: orgLevel, ratio: orgRatio, status: orgLabels[orgLevel].status, description: orgLabels[orgLevel].desc, criteria: orgCriteria },
        { label: 'Completeness', level: compLevel, ratio: compRatio, status: compLabels[compLevel].status, description: compLabels[compLevel].desc, criteria: compCriteria },
        { label: 'Professionalism', level: profLevel, ratio: profRatio, status: profLabels[profLevel].status, description: profLabels[profLevel].desc, criteria: profCriteria }
    ];

    return breakdown;
});

const scoreBreakdown = computed(() => {
    const totalPoints = parseFloat(activity.value?.total_points || 100);
    return rubricBreakdown.value.map(r => ({
        label: r.label,
        score: r.ratio * (totalPoints / 5),
        max: totalPoints / 5
    }));
});
const getBarColorForLevel = (level) => {
    if (level >= 4) return 'bg-[#10B981]'; // Green
    if (level >= 3) return 'bg-[#F59E0B]'; // Orange
    return 'bg-[#EF4444]'; // Red
};

const calculatedScore = computed(() => {
    const totalPoints = parseFloat(activity.value?.total_points || 100);
    const sumOfRatios = rubricBreakdown.value.reduce((acc, r) => acc + r.ratio, 0);
    // Each rubric contributes 1/5th of the total points if its ratio is 1.
    // So, sumOfRatios (max 5) * (totalPoints / 5)
    return sumOfRatios * (totalPoints / 5);
});

// Explicitly FORCE the backend to save this exact calculated score so
// it isn't overridden by a generic backend completion score on release.
// Scoring Enforcement Watcher Removed - Rely on Backend Source of Truth

onMounted(fetchData);

const goBack = () => router.push(`/instructor/activity/${activityId}`);

const formatDueDate = (date) => {
    if (!date) return 'TBA';
    return new Date(date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
};

const isPassengerPerfect = (p) => {
    return Object.values(p).every(field => field.isMet);
};

const getBarColor = (score, max) => {
    const ratio = score / max;
    if (ratio >= 0.8) return 'bg-[#10B981]'; // Green
    if (ratio >= 0.5) return 'bg-[#F59E0B]'; // Orange/Yellow
    return 'bg-[#EF4444]'; // Red
};

const formatTripType = (type) => {
    if (!type) return '-';
    // Remove hardcoded map, just clean up the raw string (e.g. "one_way" -> "One Way")
    return type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
};

const formatClass = (cls) => {
    if (!cls) return '-';
    // Remove hardcoded map, just return the raw string from backend
    return typeof cls === 'string' ? cls.trim() : String(cls);
};

const formatTravelClass = (tc) => {
    if(!tc) return 'Any';
    switch(tc.toLowerCase()) {
        case 'economy': return 'Economy';
        case 'premium_economy': return 'Premium Economy';
        case 'business': return 'Business Class';
        case 'first': return 'First Class';
        default: return tc;
    }
};

const actualClass = computed(() => {
    if (!booking.value?.details || booking.value.details.length === 0) return 'N/A';
    
    // Collect unique seat classes (Travel Class) from ALL booking details.
    // ONLY read from seat_class_name (the SeatClass FK) — NOT fare_family_name (that's the Ticket Bundle).
    const uniqueClasses = new Set();
    booking.value.details.forEach(d => {
        // Priority 1: seat_class FK on the detail
        // Priority 2: seat_class FK on the seat itself
        const raw = d.seat_class_name || d.seat?.seat_class_name || null;
        if (raw && typeof raw === 'string') {
            uniqueClasses.add(formatTravelClass(raw.trim()));
        }
    });

    if (uniqueClasses.size === 0) return 'NOT SPECIFIED';
    const list = Array.from(uniqueClasses);
    return list.length === 1 ? list[0] : `Mixed (${list.join(', ')})`;
});

const actualFareType = computed(() => {
    if (!booking.value?.details || booking.value.details.length === 0) return 'N/A';
    
    // Dynamically collect unique fare family names from ALL segments
    const uniqueFares = new Set();
    booking.value.details.forEach(d => {
        const raw = d.fare_family_name || null;
        if (raw && typeof raw === 'string') {
            uniqueFares.add(normalizeFareName(raw));
        }
    });

    if (uniqueFares.size === 0) return 'NOT SPECIFIED';
    const list = Array.from(uniqueFares);
    return list.length === 1 ? list[0] : `Mixed (${list.join(', ')})`;
});

const actualOrigin = computed(() => {
    if (!actualSegments.value || actualSegments.value.length === 0) return 'NOT BOOKED';
    return actualSegments.value[0].origin || 'NOT BOOKED';
});

const actualDestination = computed(() => {
    if (!actualSegments.value || actualSegments.value.length === 0) return 'NOT BOOKED';
    // For one-way: last segment destination. For round-trip: first leg's destination (outbound end).
    const normType = normalizedTripType.value;
    if (normType === 'round_trip' && actualSegments.value.length > 1) {
        return actualSegments.value[0].destination || 'NOT BOOKED';
    }
    return actualSegments.value[actualSegments.value.length - 1].destination || 'NOT BOOKED';
});

const actualDepartureDate = computed(() => {
    if (!actualSegments.value || actualSegments.value.length === 0) return 'NOT BOOKED';
    return actualSegments.value[0].departure_date || 'NOT BOOKED';
});

const actualRoute = computed(() => {
    if (!actualSegments.value || actualSegments.value.length === 0) return null;
    const segments = actualSegments.value;
    if (segments.length === 1) {
        return `${segments[0].origin} → ${segments[0].destination}`;
    }
    const cities = [segments[0].origin];
    segments.forEach(seg => {
        if (cities[cities.length - 1] !== seg.destination) {
            cities.push(seg.destination);
        }
    });
    return cities.join(' → ');
});

const requiredRoute = computed(() => {
    if (!activity.value) return '-';
    const type = (activity.value.required_trip_type || '').toLowerCase().replace(/[\s_]/g, '');
    
    if (type === 'multicity' && activity.value.segments?.length) {
        const cities = [activity.value.segments[0].origin];
        activity.value.segments.forEach(seg => {
            if (cities[cities.length - 1] !== seg.destination) {
                cities.push(seg.destination);
            }
        });
        return cities.join(' → ');
    } else if (type === 'roundtrip') {
        return `${activity.value.required_origin} ↔ ${activity.value.required_destination}`;
    }
    return `${activity.value.required_origin} → ${activity.value.required_destination}`;
});

const actualReturnDate = computed(() => {
    if (normalizedTripType.value !== 'round_trip') return null;
    if (!actualSegments.value || actualSegments.value.length < 2) return 'NOT BOOKED';
    return actualSegments.value[1].departure_date || 'NOT BOOKED';
});

const actualReturnOrigin = computed(() => {
    if (normalizedTripType.value !== 'round_trip') return null;
    if (!actualSegments.value || actualSegments.value.length < 2) return 'NOT BOOKED';
    return actualSegments.value[1].origin || 'NOT BOOKED';
});

const actualReturnDestination = computed(() => {
    if (normalizedTripType.value !== 'round_trip') return null;
    if (!actualSegments.value || actualSegments.value.length < 2) return 'NOT BOOKED';
    return actualSegments.value[1].destination || 'NOT BOOKED';
});

const normalizeDate = (d) => {
    if (!d) return null;
    let ds = '';
    if (d instanceof Date) ds = d.toISOString();
    else ds = String(d);
    const match = ds.match(/(\d{4}-\d{2}-\d{2})/);
    return match ? match[1] : ds.split('T')[0].trim();
};

// Strict exact match (case-insensitive, trimmed). One wrong character = FAIL.
const compareStrings = (a, b) => {
    const s1 = (a || '').toString().trim().toLowerCase();
    const s2 = (b || '').toString().trim().toLowerCase();
    return s1 === s2;
};

const formatGender = (g) => {
    if (!g) return '-';
    const val = g.toLowerCase().trim();
    if (val === 'mr' || val === 'male') return 'Mr.';
    if (val === 'mrs' || val === 'female') return 'Mrs.';
    if (val === 'ms') return 'Ms.';
    return g.charAt(0).toUpperCase() + g.slice(1);
};

const compareGender = (g1, g2) => {
    if (!g1 || !g2) return false;
    const v1 = g1.toLowerCase().trim().replace('.', '');
    const v2 = g2.toLowerCase().trim().replace('.', '');
    
    const isMale1 = (v1 === 'mr' || v1 === 'male');
    const isMale2 = (v2 === 'mr' || v2 === 'male');
    
    const isFemale1 = (v1 === 'mrs' || v1 === 'female' || v1 === 'ms');
    const isFemale2 = (v2 === 'mrs' || v2 === 'female' || v2 === 'ms');
    
    if (isMale1 && isMale2) return true;
    if (isFemale1 && isFemale2) return true;
    return v1 === v2;
};

/**
 * Normalizes fare bundle names by stripping redundant travel class prefixes.
 * e.g., "PREMIUM ECONOMY PREMIUM SAVER" -> "PREMIUM SAVER"
 *       "ECONOMY SAVER" -> "SAVER"
 */
const normalizeFareName = (name) => {
    if (!name) return '';
    let val = name.toLowerCase().trim();
    
    const classTerms = [
        'economy class', 'premium economy', 'comfort class', 'business class', 'first class',
        'economy', 'business', 'first', 'comfort'
    ];
    
    // Sort by length descending to match longest terms first
    classTerms.sort((a,b) => b.length - a.length).forEach(term => {
        // Case 1: Prefix at the start (e.g., "Economy Saver")
        if (val.startsWith(term + ' ')) {
            val = val.substring(term.length).trim();
        } 
        // Case 2: Suffix or middle (e.g., "Flex Economy")
        else if (val.includes(' ' + term)) {
            val = val.replace(new RegExp('\\b' + term + '\\b', 'g'), '').trim();
        }
    });
    
    return val.toUpperCase();
};

const actualPaxTypes = computed(() => {
    const types = { adult: 0, child: 0, infant: 0 };
    const seenPassengers = new Set();
    
    booking.value?.details?.forEach(detail => {
        const pId = detail.passenger?.id || `${detail.passenger?.first_name}_${detail.passenger?.last_name}_${detail.passenger?.date_of_birth}`;
        if (seenPassengers.has(pId)) return;
        seenPassengers.add(pId);

        const type = (detail.passenger_type || detail.passenger?.type || 'adult').toLowerCase();
        if (type === 'adult') types.adult++;
        else if (type === 'child') types.child++;
        else if (type === 'infant') types.infant++;
    });
    return types;
});

// Helper: extract the Travel Class (seat class) from a booking detail record.
// ONLY reads from seat_class.name (the FK relationship).
// fare_family_name is the Ticket Bundle/Fare Type — completely different — do NOT use it here.
const extractTravelClass = (detail) => {
    // 1. seat_class FK serialized directly on the booking detail
    if (detail?.seat_class_name && typeof detail.seat_class_name === 'string') {
        return detail.seat_class_name.trim();
    }
    // 2. seat_class FK from the associated seat object
    if (detail?.seat?.seat_class_name && typeof detail.seat.seat_class_name === 'string') {
        return detail.seat.seat_class_name.trim();
    }
    // Cannot determine travel class — return null so the UI shows "NOT SPECIFIED"
    return null;
};

// Build actual booking segments (one unique entry per flight leg, sorted by departure_time)
const actualSegments = computed(() => {
    if (!booking.value?.details) return [];
    // Deduplicate by schedule id to avoid passenger-per-row inflation
    const seen = new Set();
    const segs = [];
    // Sort all details by departure_time so outbound always comes before return
    const sortedDetails = [...booking.value.details].sort((a, b) => {
        const tA = a.schedule?.departure_time || '';
        const tB = b.schedule?.departure_time || '';
        return tA < tB ? -1 : tA > tB ? 1 : 0;
    });
    for (const d of sortedDetails) {
        if (!d.schedule?.origin) continue;
        const uniqueKey = d.schedule.id
            ? String(d.schedule.id)
            : `${d.schedule.origin}_${d.schedule.destination}_${d.schedule.departure_time}`;
        if (!seen.has(uniqueKey)) {
            seen.add(uniqueKey);
            segs.push({
                origin: d.schedule.origin || '-',
                destination: d.schedule.destination || '-',
                departure_date: d.schedule.departure_time
                    ? String(d.schedule.departure_time).split('T')[0].split(' ')[0]
                    : '-',
                // Use extractTravelClass helper so both seat_class_name and fare_family_name are checked
                seat_class_name: extractTravelClass(d)
            });
        }
    }
    return segs;
});

const matches = computed(() => {
    if (!activity.value || !booking.value) return {
        passenger_details: [],
        addons: [],
        segments: []
    };
    
    // Normalize BOTH trip types to raw code form for comparison
    // activity.required_trip_type may be a display value like "One Way" from Django's get_display()
    // booking.trip_type is always the raw code like "one_way"
    const reqTripTypeNorm = normalizeTripTypeToCode(activity.value.required_trip_type || '');
    const actTripTypeNorm = normalizeTripTypeToCode(booking.value.trip_type || '');
    const isRoundTrip = reqTripTypeNorm === 'round_trip';

    const m = {
        trip_type: reqTripTypeNorm === actTripTypeNorm,
        origin: compareStrings(activity.value.required_origin, actualOrigin.value),
        destination: compareStrings(activity.value.required_destination, actualDestination.value),
        return_origin: !isRoundTrip || compareStrings(activity.value.required_destination, actualReturnOrigin.value),
        return_destination: !isRoundTrip || compareStrings(activity.value.required_origin, actualReturnDestination.value),
        fare_type: (() => {
            const reqFare = activity.value.required_seat_class;
            if (!reqFare || reqFare.toLowerCase() === 'any' || reqFare.toLowerCase() === 'na') return true;
            if (!booking.value?.details?.length) return false;
            
            // Normalize and compare both sides to strip class redundancies
            const normReq = normalizeFareName(reqFare);
            return booking.value.details.every(d => normalizeFareName(d.fare_family_name) === normReq);
        })(),
        travel_class: (() => {
            // Strict exact match: normalize by removing spaces/underscores/hyphens/dots and the word 'class'
            const norm = (s) => (s || '').toLowerCase().replace(/[\s_\-\.]/g, '').replace('class', '').trim();
            const reqClass = norm(activity.value.required_travel_class || 'economy');
            if (!reqClass || reqClass === 'na' || reqClass === 'n/a') return true;

            // Every single booking detail segment must exactly match the required class
            if (!booking.value?.details?.length) return false;
            
            return booking.value.details.every(d => {
                // Only read the actual seat class name — NOT fare_family_name (that's Ticket Bundle)
                const rawName = d.seat_class_name || d.seat?.seat_class_name || '';
                if (!rawName) return false;
                const actualNorm = norm(rawName);
                // Strict exact match only — one wrong class = FAIL
                return actualNorm === reqClass;
            });
        })(),
        departure_date: !activity.value.required_departure_date || normalizeDate(activity.value.required_departure_date) === normalizeDate(actualDepartureDate.value),
        return_date: !isRoundTrip || !activity.value.required_return_date || normalizeDate(activity.value.required_return_date) === normalizeDate(actualReturnDate.value),
        pax_types: (actualPaxTypes.value.adult || 0) === (activity.value.required_passengers || 0) && 
                   (actualPaxTypes.value.child || 0) === (activity.value.required_children || 0) && 
                   (actualPaxTypes.value.infant || 0) === (activity.value.required_infants || 0),
        passenger_details: [],
        addons: [],
        segments: []   // per-route match results for multi-city
    };

    // Multi-city segment matching
    if (reqTripTypeNorm === 'multi_city' && activity.value.segments?.length) {
        activity.value.segments.forEach((expected, idx) => {
            // Find the best matching actual segment regardless of index order
            let actualMatched = actualSegments.value.find(as => 
                compareStrings(expected.origin, as.origin) && 
                compareStrings(expected.destination, as.destination)
            );
            
            const originMatched = actualMatched ? true : (actualSegments.value[idx] ? compareStrings(expected.origin, actualSegments.value[idx].origin) : false);
            const destMatched = actualMatched ? true : (actualSegments.value[idx] ? compareStrings(expected.destination, actualSegments.value[idx].destination) : false);

            if (!actualMatched) {
                // Fallback to positional matching
                actualMatched = actualSegments.value[idx] || null;
            }
            
            // If we found it, check the date too
            const dateMatched = actualMatched ? (!expected.departure_date || normalizeDate(expected.departure_date) === normalizeDate(actualMatched.departure_date)) : false;

            // Strict per-leg travel class check for multi-city
            const norm = (s) => (s || '').toLowerCase().replace(/[\s_\-\.]/g, '').replace('class', '').trim();
            const reqClass = norm(activity.value.required_travel_class || 'economy');
            const legClass = actualMatched?.seat_class_name || null;
            // Exact match only — one wrong class code = FAIL for this leg
            const classMatched = actualMatched
                ? (reqClass === 'na' || reqClass === 'n/a' || reqClass === ''
                    ? true
                    : (legClass ? norm(legClass) === reqClass : false))
                : false;

            m.segments.push({
                origin: originMatched,
                destination: destMatched,
                departure_date: dateMatched,
                travel_class: classMatched,
                actualData: actualMatched // Map exactly what the student picked for this leg
            });
        });
    }

    // 1. Passenger Identities (Stateful Matching)
    const bookedPassengers = [];
    const seenPId = new Set();
    booking.value.details?.forEach(d => {
        if (!d.passenger) return;
        const pId = d.passenger.id || `${d.passenger.first_name}_${d.passenger.last_name}`;
        if (!seenPId.has(pId)) {
            seenPId.add(pId);
            bookedPassengers.push(d.passenger);
        }
    });

    const usedIndices = new Set();
    if (activity.value.passengers) {
        activity.value.passengers.forEach(expected => {
            // Find match among unused booked passengers
            let actualIdx = bookedPassengers.findIndex((p, idx) => 
                !usedIndices.has(idx) && 
                p.first_name?.toLowerCase().trim() === expected.first_name?.toLowerCase().trim() && 
                p.last_name?.toLowerCase().trim() === expected.last_name?.toLowerCase().trim() &&
                (p.middle_name?.toLowerCase().trim() || '') === (expected.middle_name?.toLowerCase().trim() || '')
            );

            // Fallback to positional to display actual student work
            if (actualIdx === -1) {
                actualIdx = bookedPassengers.findIndex((p, idx) => !usedIndices.has(idx));
            }

            let actual = null;
            if (actualIdx !== -1) {
                actual = bookedPassengers[actualIdx];
                usedIndices.add(actualIdx);
            }

            const detailMatch = {
                name: { 
                    expected: `${expected.first_name} ${expected.middle_name ? expected.middle_name + ' ' : ''}${expected.last_name}`.toUpperCase().trim(), 
                    actual: actual ? `${actual.first_name} ${actual.middle_name ? actual.middle_name + ' ' : ''}${actual.last_name}`.toUpperCase().trim() : 'NOT SET', 
                    // Strict: every part of the name must match exactly — one letter off = FAIL
                    isMet: actual
                        ? (actual.first_name?.toLowerCase().trim() === expected.first_name?.toLowerCase().trim() &&
                           actual.last_name?.toLowerCase().trim() === expected.last_name?.toLowerCase().trim() &&
                           (actual.middle_name?.toLowerCase().trim() || '') === (expected.middle_name?.toLowerCase().trim() || ''))
                        : false
                },
                passengerType: {
                    expected: (() => {
                        const pt = (expected.passenger_type || 'adult').toLowerCase();
                        return pt.charAt(0).toUpperCase() + pt.slice(1);
                    })(),
                    actual: (() => {
                        if (!actual) return 'NOT BOOKED';
                        const pt = (actual.passenger_type || actual.type || 'adult').toLowerCase();
                        return pt.charAt(0).toUpperCase() + pt.slice(1);
                    })(),
                    isMet: false
                },
                gender: { 
                    expected: formatGender(expected.gender), 
                    actual: formatGender(actual?.title || actual?.gender), 
                    isMet: compareGender(expected.gender, actual?.title || actual?.gender) 
                },
                dob: { 
                    expected: expected.date_of_birth, 
                    actual: actual?.date_of_birth || '-', 
                    isMet: false 
                },
                nationality: { 
                    expected: expected.nationality || '-', 
                    actual: actual ? (actual.nationality || 'NOT SET') : 'NOT BOOKED', 
                    isMet: false 
                },
                category: {
                    // Map stored codes to human-readable labels (must match booking form labels)
                    expected: (() => {
                        const cat = (expected.passenger_category || 'none').toLowerCase();
                        if (cat === 'senior' || cat === 'senior citizen') return 'Senior Citizen';
                        if (cat === 'pwd') return 'PWD';
                        return 'Regular (None)';
                    })(),
                    actual: (() => {
                        if (!actual) return 'NOT BOOKED';
                        const disc = (actual.ph_discount_type ?? 'none').toLowerCase();
                        if (disc === 'senior' || disc === 'senior citizen') return 'Senior Citizen';
                        if (disc === 'pwd') return 'PWD';
                        return 'Regular (None)';
                    })(),
                    isMet: false
                },
                passport: { 
                    expected: activity.value.require_passport ? (expected.passport_number || 'REQUIRED') : 'NO PASSPORT REQ.', 
                    actual: actual?.passport_number || 'NONE', 
                    isMet: !activity.value.require_passport // Always met if not required
                },
                    seating: (() => {
                        const isInfant = (expected.type || expected.passenger_type || '').toLowerCase() === 'infant';
                        const tripType = normalizeTripTypeToCode(activity.value?.required_trip_type || '');

                        if (isInfant) {
                            return {
                                expected: expected.associated_adult_index ? `Adult ${expected.associated_adult_index}` : 'ANY',
                                actual: actual?.associated_adult ? `Adult ${actual.associated_adult}` : 'N/A',
                                isMet: false // resolved below in if(actual) block
                            };
                        }

                        // Robust seat lookup: match by name (works for all trip types)
                        // For multi-city, a passenger has one detail per leg — collect ALL seat numbers
                        const passengerDetails = (booking.value?.details || []).filter(d => {
                            if (!d.passenger) return false;
                            const fn = (d.passenger.first_name || '').toLowerCase().trim();
                            const ln = (d.passenger.last_name || '').toLowerCase().trim();
                            const efn = (actual?.first_name || '').toLowerCase().trim();
                            const eln = (actual?.last_name || '').toLowerCase().trim();
                            // Match by id first, then fall back to name
                            return (d.passenger.id && actual?.id && d.passenger.id === actual.id)
                                || (fn === efn && ln === eln && fn !== '' && ln !== '');
                        });

                        // Collect all assigned seat numbers (filter out null/empty)
                        const assignedSeats = passengerDetails
                            .map(d => d.seat_number || d.seat?.seat_number || null)
                            .filter(s => s && String(s).trim() !== '');

                        const seatDisplay = assignedSeats.length > 0
                            ? assignedSeats.join(' / ')
                            : 'N/A';

                        // For multi-city: every leg must have a seat
                        // For one-way/round-trip: at least one seat must be selected
                        const isMet = tripType === 'multi_city'
                            ? (passengerDetails.length > 0 && assignedSeats.length === passengerDetails.length)
                            : assignedSeats.length > 0;

                        return {
                            expected: 'ANY AVAILABLE SEAT',
                            actual: seatDisplay,
                            isMet
                        };
                    })(),
                addons: {
                    expected: '', // Will be populated below
                    actual: 'N/A',
                    isMet: true
                }
            };

            // Population for Add-ons inside Passenger Detail
            const passengerAddons = activity.value.activity_addons?.filter(ra => 
                (ra.passenger?.first_name?.toLowerCase() === expected.first_name?.toLowerCase() && 
                 ra.passenger?.last_name?.toLowerCase() === expected.last_name?.toLowerCase()) ||
                (ra.passenger_index !== undefined && activity.value.passengers.indexOf(expected) === ra.passenger_index)
            ) || [];

            if (passengerAddons.length > 0) {
                detailMatch.addons.expected = passengerAddons.map(ra => ra.addon_name || ra.addon?.name).join('<br/>') || 'None';
                
                // Find actual addons for this specific passenger booking detail
                const passengerBookingDetail = booking.value.details?.find(d => 
                    d.passenger?.first_name?.toLowerCase() === expected.first_name?.toLowerCase() &&
                    d.passenger?.last_name?.toLowerCase() === expected.last_name?.toLowerCase()
                );

                if (passengerBookingDetail) {
                    detailMatch.addons.actual = passengerBookingDetail.addons?.map(a => a.name).join(', ') || 'N/A';
                    detailMatch.addons.isMet = passengerAddons.every(ra => 
                        passengerBookingDetail.addons?.some(a => a.id === ra.addon_id || a.name === ra.addon_name)
                    );
                } else {
                    detailMatch.addons.isMet = false;
                }
            } else {
                detailMatch.addons.expected = 'None Required';
                detailMatch.addons.actual = 'N/A';
                detailMatch.addons.isMet = true;
            }

            if (actual) {
                // Strict Gender/Title matching: compare the exact title code (mr, mrs, ms).
                // MRS ≠ MS — one wrong letter = FAIL. No grouping all females together.
                const normG = (s) => (s || '').toLowerCase().replace(/[.\s]/g, '').trim();
                const actualTitle = normG(actual.title || actual.gender || '');
                const expectedGender = normG(expected.gender || '');
                // Exact code match — both sides must resolve to the same title code
                detailMatch.gender.isMet = (actualTitle === expectedGender);
                
                detailMatch.dob.isMet = normalizeDate(actual.date_of_birth) === normalizeDate(expected.date_of_birth);
                // Nationality: strict case-insensitive match
                detailMatch.nationality.isMet = !!actual.nationality && 
                    (actual.nationality || '').toLowerCase().trim() === (expected.nationality || '').toLowerCase().trim();
                
                // Improved Lenient Category matching
                const normC = (s) => (s || '').toLowerCase().replace(/[\s_\-\.]/g, '').replace('(none)', '').replace('citizen', '').trim();
                const actCat = normC(actual.ph_discount_type || 'none');
                const expCat = normC(expected.passenger_category || 'none');
                
                const isS = (c) => c.includes('senior');
                const isP = (c) => c.includes('pwd');
                const isR = (c) => !isS(c) && !isP(c);
                
                if (isS(expCat)) detailMatch.category.isMet = isS(actCat);
                else if (isP(expCat)) detailMatch.category.isMet = isP(actCat);
                else detailMatch.category.isMet = isR(actCat);

                // Passenger Type Validation
                const _actualType = (actual.passenger_type || actual.type || 'adult').toLowerCase().trim();
                const _expectedType = (expected.passenger_type || 'adult').toLowerCase().trim();
                detailMatch.passengerType.isMet = _actualType === _expectedType;

                
                if (activity.value.require_passport) {
                    detailMatch.passport.isMet = (actual.passport_number || '').trim() === (expected.passport_number || '').trim();
                }

                if ((expected.type || expected.passenger_type || '').toLowerCase() === 'infant') {
                    // Infant must be associated with the correct adult seat
                    detailMatch.seating.isMet = String(actual.associated_adult) === String(expected.associated_adult_index);
                }
                // NOTE: Non-infant seating isMet is already resolved inline in the seating block above
            }
            m.passenger_details.push(detailMatch);
        });
    }

    // 2. Add-ons Verification — works for ALL trip types (one-way, round-trip, multi-city)
    //
    // WHY NORMALIZATION IS NEEDED:
    //   - Activity required addon name (from ActivityAddon → AddOn.name): "Ceb Wheelchair Service"
    //   - Booking detail addon name (from AddOn.get_or_create defaults): "Assistance: Ceb Wheelchair Service"
    // The backend adds a category prefix ("Assistance: ", "Meal: ", "Extra Baggage ") when creating booking AddOns.
    // We must strip these prefixes before comparing so the names match correctly.
    const normalizeAddonName = (name) => {
        return (name || '')
            .toLowerCase()
            .replace(/^assistance:\s*/i, '')
            .replace(/^assistance service:\s*/i, '')
            .replace(/^meal:\s*/i, '')
            .replace(/^extra baggage\s*/i, '')  // "Extra Baggage 20kg" → "20kg"
            .replace(/extra baggage/i, 'baggage') // catch other formats
            .replace(/\s*(kg|kgs)([\s_-])/gi, 'kg ')
            .trim();
    };

    // Check if a required addon matches a student's actual addon (multi-strategy)
    const addonMatches = (reqName, reqId, actualAddon) => {
        // 1. Direct AddOn ID match (most reliable, works if IDs happen to be the same)
        if (reqId && actualAddon.id === reqId) return true;

        const normReq    = normalizeAddonName(reqName);
        const normActual = normalizeAddonName(actualAddon.name);

        if (!normReq || !normActual) return false;

        // 2. Normalized exact match — same name after stripping prefixes
        if (normReq === normActual) return true;

        // 3. Substring match as fallback (one contains the other)
        // e.g., "20kg extra baggage" ↔ "20kg" should still match
        if (normReq.length >= 3 && normActual.length >= 3) {
            if (normReq.includes(normActual) || normActual.includes(normReq)) return true;
        }

        return false;
    };

    if (activity.value.activity_addons?.length) {
        activity.value.activity_addons.forEach(req => {
            const reqFirstName = (req.passenger?.first_name || '').toLowerCase().trim();
            const reqLastName  = (req.passenger?.last_name  || '').toLowerCase().trim();

            // Collect ALL booking detail records for this passenger across every leg
            // This is critical for multi-city where one passenger has N detail records
            const allPassengerDetails = (booking.value?.details || []).filter(d => {
                const fn = (d.passenger?.first_name || '').toLowerCase().trim();
                const ln = (d.passenger?.last_name  || '').toLowerCase().trim();
                return fn === reqFirstName && ln === reqLastName && fn !== '';
            });

            // Gather ALL unique addons this passenger selected (across all legs)
            const allActualAddons = [];
            const seenAddonIds = new Set();
            allPassengerDetails.forEach(d => {
                (d.addons || []).forEach(a => {
                    const key = String(a.id || a.name || '');
                    if (key && !seenAddonIds.has(key)) {
                        seenAddonIds.add(key);
                        allActualAddons.push(a);
                    }
                });
            });

            const reqAddonName = req.addon_name || req.addon?.name || '';
            const reqAddonId   = req.addon_id    || null;

            // Check using multi-strategy match (ID → normalized name → substring)
            const isMet = allActualAddons.some(a => addonMatches(reqAddonName, reqAddonId, a));

            // Display: show all actual addons selected by the student, or "NONE"
            const actualDisplay = allActualAddons.length > 0
                ? allActualAddons.map(a => a.name).join(', ')
                : 'NONE';

            m.addons.push({
                passengerName: `${req.passenger?.first_name || ''} ${req.passenger?.last_name || ''}`.trim(),
                requirement: reqAddonName || 'Required Add-on',
                actual: actualDisplay,
                isMet
            });
        });
    }

    return m;
});

const findMatchingPassenger = (expected) => {
    if (!booking.value?.details) return null;
    
    // 1. Try exact name match
    const exact = booking.value.details?.find(d => 
        d.passenger?.first_name?.toLowerCase() === expected.first_name?.toLowerCase() &&
        d.passenger?.last_name?.toLowerCase() === expected.last_name?.toLowerCase()
    );
    if (exact) return exact.passenger;

    // 2. Collect unique passengers from booking
    const uniquePassengers = [];
    const seenIds = new Set();
    booking.value.details?.forEach(d => {
        if (!d.passenger) return;
        const id = d.passenger.id || `${d.passenger.first_name}_${d.passenger.last_name}`;
        if (!seenIds.has(id)) {
            seenIds.add(id);
            uniquePassengers.push(d.passenger);
        }
    });

    const idx = activity.value.passengers.indexOf(expected);
    return uniquePassengers[idx] || null;
};

const comparisonRows = computed(() => {
    if (!activity.value) return [];
    
    // Normalize trip type for comparison
    const rawTripType = (activity.value.required_trip_type || '').toLowerCase();
    const reqTripType = rawTripType.replace(/\s+/g, '_');
    const isMultiCity = reqTripType === 'multi_city';
    
    const m = booking.value ? matches.value : {
        trip_type: false,
        origin: false,
        destination: false,
        return_origin: false,
        return_destination: false,
        travel_class: false,
        departure_date: false,
        return_date: false,
        pax_types: false
    };

    const rows = [
        { 
            label: 'Trip Type', 
            priority: 'High', 
            requirement: formatTripType(activity.value.required_trip_type), 
            work: booking.value ? formatTripType(booking.value.trip_type) : 'NOT BOOKED', 
            isMet: m.trip_type 
        },
        { 
            label: 'Passengers', 
            priority: 'High', 
            requirement: [
                `${activity.value.required_passengers || 0} Adult(s)`,
                activity.value.required_children ? `${activity.value.required_children} Child(ren)` : '',
                activity.value.required_infants ? `${activity.value.required_infants} Infant(s)` : ''
            ].filter(Boolean).join(', '),
            work: booking.value ? [
                `${actualPaxTypes.value.adult || 0} Adult(s)`,
                actualPaxTypes.value.child ? `${actualPaxTypes.value.child} Child(ren)` : '',
                actualPaxTypes.value.infant ? `${actualPaxTypes.value.infant} Infant(s)` : ''
            ].filter(Boolean).join(', ') : 'NOT BOOKED',
            isMet: m.pax_types
        },
        { label: 'Travel Class', priority: 'High', requirement: formatTravelClass(activity.value.required_travel_class), work: actualClass.value !== 'N/A' ? actualClass.value : 'NOT BOOKED', isMet: m.travel_class },
        { 
            label: 'Infant Seating', 
            priority: 'High', 
            requirement: activity.value.required_infants ? 'Correct adult assignment' : 'N/A', 
            work: activity.value.required_infants 
                ? (m.passenger_details?.filter(p => p.seating.expected !== 'N/A' && p.seating.isMet).length === m.passenger_details?.filter(p => p.seating.expected !== 'N/A').length ? 'All assigned' : 'Wrong assignment')
                : 'N/A', 
            isMet: activity.value.required_infants 
                ? (m.passenger_details?.filter(p => p.seating.expected !== 'N/A').length > 0 && m.passenger_details?.filter(p => p.seating.expected !== 'N/A').every(p => p.seating.isMet))
                : true
        }
    ];

    if (isMultiCity && activity.value.segments?.length) {
        // Multi-city uses its own visual blocks
        // We only show basic configuration here
    } else {
        // Route-specific validations are handled in their own explicit visual components
        // The Compliance table strictly handles Configuration settings (Class, Passengers, Trip Type)
    }

    return rows;
});


</script>

<style scoped>
@keyframes loading {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(300%); }
}
</style>
