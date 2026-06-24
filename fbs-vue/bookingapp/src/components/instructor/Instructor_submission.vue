<template>
  <div class="instructor-submission">
    <!-- Submissions Header -->
    <div class="flex items-center justify-between mb-8 print:hidden">
      <h2 class="text-2xl font-black text-gray-900 uppercase tracking-tight">Student Submissions</h2>
      <div class="flex items-center gap-4">
        <!-- SHOW GRADE button — ALWAYS VISIBLE as requested. Badge count shows if there are pending students to reveal. -->
        <button 
          @click="revealGrades"
          :class="['text-[10px] font-bold text-white px-3 py-1.5 uppercase tracking-widest flex items-center gap-1.5 rounded-md transition-all shadow-sm',
                   hasHiddenGrades ? 'bg-pink-500 hover:bg-pink-600' : 'bg-pink-300 cursor-not-allowed border border-pink-200/50 shadow-none']"
          :disabled="!hasHiddenGrades"
        >
          <span>SHOW GRADE</span>
          <span class="bg-white/90 text-pink-600 text-[8px] font-black px-1 py-0.5 rounded-sm drop-shadow-sm leading-none">{{ pendingHiddenCount }}</span>
        </button>

        <!-- RELEASE GRADES button — For sending to student's dashboard -->
        <button 
          v-if="absoluteUnreleasedCount > 0"
          @click="$emit('release-grades', revealedStudentIds)" 
          :disabled="releasing_grades"
          class="text-[10px] font-bold bg-slate-800 text-white px-3 py-1.5 hover:bg-slate-900 uppercase tracking-widest flex items-center gap-1.5 rounded-md transition-all shadow-sm disabled:opacity-50"
        >
          <svg v-if="releasing_grades" class="animate-spin h-3 w-3 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <template v-else>
            <span>RELEASE GRADES</span>
            <span class="bg-white/90 text-slate-800 text-[8px] font-black px-1 py-0.5 rounded-sm drop-shadow-sm leading-none">{{ pendingReleaseCount }}</span>
          </template>
        </button>

        <!-- All grades released — still show a small badge so instructor knows state -->
        <div v-else-if="activity?.grades_released" 
          class="flex items-center gap-2 bg-green-50 text-green-700 px-4 py-2 rounded-lg border border-green-100">
           <span class="text-green-500 text-xs">✓</span>
           <span class="text-[9px] font-black uppercase tracking-widest">All Scores Released</span>
        </div>

        <button 
          @click="$emit('print')" 
          class="text-[10px] font-black text-green-600 hover:text-green-800 uppercase tracking-widest flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          Print Report
        </button>

        <button 
          @click="$emit('refresh')" 
          class="text-[10px] font-black text-blue-600 hover:text-blue-800 uppercase tracking-widest flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" :class="['h-3 w-3', submissions_loading ? 'animate-spin' : '']" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Top 5 Leaderboard Highlights -->
    <div v-if="topStudents.length > 0" class="mb-8 mt-6 print:hidden" style="display:grid; grid-template-columns: repeat(5, 1fr); gap: 1rem;">
      <div v-for="(student, idx) in topStudents.slice(0, 5)" :key="student.student_id" 
        class="flex items-center gap-3 px-4 py-2.5 rounded-2xl border bg-white transition-all shadow-sm hover:shadow-md"
        :class="[
          idx === 0 ? 'border-amber-200 bg-amber-50/20 shadow-amber-100/20' : 
          idx === 1 ? 'border-slate-200 bg-gray-50/10' : 
          'border-gray-100 hover:border-gray-200'
        ]"
      >
        <div class="relative shrink-0">
          <div :class="[
            'w-10 h-10 rounded-full flex items-center justify-center text-lg shadow-inner border border-black/5',
            idx === 0 ? 'bg-amber-400 text-white' : idx === 1 ? 'bg-slate-300 text-white' : idx === 2 ? 'bg-orange-300 text-white' : 'bg-gray-100 text-gray-500'
          ]">
            {{ idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : (idx + 1) }}
          </div>
          <div v-if="idx === 0" class="absolute -top-1.5 -right-1.5 text-[10px] drop-shadow-sm">👑</div>
        </div>
        <div class="truncate">
          <p class="text-[8px] font-black uppercase tracking-widest leading-none mb-1" :class="idx === 0 ? 'text-amber-600' : 'text-gray-400'">{{ getRankWithSuffix(idx + 1) }} Place</p>
          <h4 class="text-xs font-bold text-gray-900 leading-tight truncate">{{ student.first_name }} {{ student.last_name }}</h4>
          <p class="text-[11px] font-black mt-0.5" :class="idx === 0 ? 'text-amber-700' : 'text-gray-600'">{{ getPercentage(student) }}%</p>
        </div>
      </div>
    </div>

    <!-- Quick Insights Bar -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10 print:hidden">
      <div class="bg-slate-900 rounded-2xl p-4 text-white shadow-xl flex items-center gap-4">
        <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center text-xl">📊</div>
        <div>
          <p class="text-[9px] font-black uppercase tracking-widest text-white/50">Class Avg</p>
          <p class="text-xl font-black">{{ classAverage }}%</p>
        </div>
      </div>
      <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm flex items-center gap-4">
        <div class="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center text-xl border border-green-100">✅</div>
        <div>
          <p class="text-[9px] font-black uppercase tracking-widest text-gray-400">Pass Rate</p>
          <p class="text-xl font-black text-green-600">{{ passRate }}%</p>
          <p class="text-[8px] text-gray-400 font-bold mt-0.5 uppercase tracking-tighter">{{ passedCount }} / {{ totalStudents }} Pass</p>
        </div>
      </div>
      <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm flex items-center gap-4">
        <div class="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-xl border border-blue-100">📝</div>
        <div>
          <p class="text-[9px] font-black uppercase tracking-widest text-gray-400">Participation</p>
          <p class="text-xl font-black text-blue-600">{{ participationRate }}%</p>
          <p class="text-[8px] text-gray-400 font-bold mt-0.5 uppercase tracking-tighter">{{ participationCount }} / {{ totalStudents }} Act.</p>
        </div>
      </div>
      <div class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm flex items-center gap-4">
        <div class="w-10 h-10 bg-pink-50 rounded-xl flex items-center justify-center text-xl border border-pink-100">⏳</div>
        <div>
          <p class="text-[9px] font-black uppercase tracking-widest text-gray-400">Wait to Release</p>
          <p class="text-xl font-black text-pink-500">{{ pendingReleaseCount }}</p>
        </div>
      </div>
    </div>

    <!-- Search & Filter Bar -->
    <div v-if="submissions.length > 0" class="flex flex-col md:flex-row gap-4 mb-6 items-center justify-between print:hidden">
      <div class="relative w-full md:w-80">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </span>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Search student name or ID..." 
          class="w-full bg-white border border-gray-200 rounded-xl py-2.5 pl-10 pr-4 text-xs font-medium focus:ring-2 focus:ring-pink-500 outline-none transition-all"
        >
      </div>
      <div class="flex gap-2">
        <button 
          v-for="f in ['all', 'passed', 'failed', 'not taken']" 
          :key="f"
          @click="filterStatus = f"
          :class="[
            'px-4 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest transition-all border',
            filterStatus === f ? 'bg-pink-500 text-white border-pink-500 shadow-md' : 'bg-white text-gray-400 border-gray-100 hover:bg-gray-50'
          ]"
        >
          {{ f }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="submissions_loading && submissions.length === 0" class="text-center py-20">
      <div class="inline-block w-8 h-8 border-4 border-pink-500 border-t-transparent rounded-full animate-spin mb-4"></div>
      <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">Loading student work...</p>
    </div>

    <!-- Empty States -->
    <div v-else-if="submissions.length === 0" class="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
      <p class="text-gray-400 text-sm italic">No students are currently enrolled in this section.</p>
    </div>

    <div v-else-if="filteredStudentWork.length === 0" class="text-center py-12 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
      <p class="text-gray-400 text-sm italic">No students match your current filter.</p>
    </div>

    <!-- Table (Chunks for Print, Single Table for UI) -->
    <div v-else>
      <div 
        v-for="(chunk, index) in (is_printing ? printChunks : [paginatedStudentWork])" 
        :key="'table-chunk-'+index"
        :style="is_printing && index < printChunks.length - 1 ? 'page-break-after: always;' : ''"
        class="overflow-hidden print:overflow-visible border border-gray-100 rounded-xl bg-white shadow-sm print:border-none print:shadow-none print:break-inside-avoid print:mb-0 mb-8 print:[&_table]:border-2 print:[&_table]:border-black print:[&_th]:border print:[&_th]:border-black print:[&_td]:border print:[&_td]:border-black print:[&_td]:text-center print:[&_th]:text-center print:[&_td]:align-middle print:[&_th]:align-middle print:[&_th]:px-1 print:[&_td]:px-1"
      >
        <!-- Print Header: Classic Form Layout (Only on first page) -->
        <div v-if="index === 0" class="hidden print:block mb-10 w-full">
          <div class="text-center mb-10">
            <h1 class="text-3xl font-black uppercase tracking-widest border-b-2 border-black pb-4">Grade Report</h1>
          </div>

          <div class="grid grid-cols-2 gap-x-12 gap-y-6">
            <div class="flex items-end gap-2">
              <span class="text-[11px] font-black uppercase whitespace-nowrap">Course Number:</span>
              <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ activity?.section_code }}</div>
            </div>
            <div class="flex items-end gap-2">
              <span class="text-[11px] font-black uppercase whitespace-nowrap">Section:</span>
              <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ activity?.section_name }}</div>
            </div>
            <div class="flex items-end gap-2">
              <span class="text-[11px] font-black uppercase whitespace-nowrap">Activity Title:</span>
              <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ activity?.title }}</div>
            </div>
            <div class="flex items-end gap-2">
              <span class="text-[11px] font-black uppercase whitespace-nowrap">Schedule:</span>
              <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ activity ? formatSchedule(activity.schedule) : '' }}</div>
            </div>
            <div class="flex items-end gap-2">
              <span class="text-[11px] font-black uppercase whitespace-nowrap">A.Y. Semester:</span>
              <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ activity?.academic_year }} - {{ activity?.semester }}</div>
            </div>
            <div class="flex items-end gap-2">
              <span class="text-[11px] font-black uppercase whitespace-nowrap">Date Printed:</span>
              <div class="border-b border-black flex-1 text-xs font-bold uppercase pb-0.5 px-2">{{ new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) }}</div>
            </div>
          </div>
        </div>

        <table class="w-full text-left border-collapse print:table-fixed">
          <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest print:text-[11px] print:text-black print:w-[25%] print:tracking-normal print:whitespace-nowrap">STUDENT</th>
            <th class="px-3 py-3 text-[9px] font-black text-gray-400 tracking-widest text-center print:text-[9px] print:text-black print:w-[12.5%] print:tracking-normal print:whitespace-nowrap">Accuracy</th>
            <th class="px-3 py-3 text-[9px] font-black text-gray-400 tracking-widest text-center print:text-[9px] print:text-black print:w-[12.5%] print:tracking-normal print:whitespace-nowrap">Tech Skill</th>
            <th class="px-3 py-3 text-[9px] font-black text-gray-400 tracking-widest text-center print:text-[9px] print:text-black print:w-[12.5%] print:tracking-normal print:whitespace-nowrap">Organization</th>
            <th class="px-3 py-3 text-[9px] font-black text-gray-400 tracking-widest text-center print:text-[9px] print:text-black print:w-[12.5%] print:tracking-normal print:whitespace-nowrap">Completeness</th>
            <th class="px-3 py-3 text-[9px] font-black text-gray-400 tracking-widest text-center print:text-[9px] print:text-black print:w-[12.5%] print:tracking-normal print:whitespace-nowrap">Professionalism</th>
            <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest print:text-[9px] print:text-black print:w-[12.5%] print:tracking-normal print:whitespace-nowrap">TOTAL GRADE</th>
            <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center print:hidden">STATUS</th>
            <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest text-center print:hidden">RELEASED</th>
            <th class="px-3 py-3 text-[9px] font-black text-gray-400 uppercase tracking-widest print:hidden text-right">ACTION</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="sub in chunk" :key="sub.student_id" class="hover:bg-gray-50/50 transition-colors cursor-pointer" @click="$emit('view-analysis', sub)">
            <td class="px-3 py-3">
              <div :class="is_printing ? 'font-bold text-xs text-gray-900 whitespace-normal break-words max-w-[200px] print:text-sm print:font-black' : 'font-bold text-xs text-gray-900 truncate max-w-[120px]'">{{ sub.first_name }} {{ sub.last_name }}</div>
              <div class="text-[9px] text-gray-400 font-medium tracking-tight uppercase print:text-xs print:font-black print:text-gray-700">{{ sub.student_number }}</div>
            </td>
            <td class="px-3 py-3 text-center">
              <span v-if="(sub.grade !== null || sub.booking || sub.is_failed_due_to_time) && revealedStudentIds.includes(sub.student_id)" class="text-[10px] font-bold print:text-sm print:font-black" :class="getRubricStats(sub).accuracy.ratio > 0 ? 'text-green-600' : 'text-gray-400'">
                {{ getRubricStats(sub).accuracy.level }}
              </span>
              <span v-else class="text-gray-300 text-[10px]">—</span>
            </td>
            <td class="px-3 py-3 text-center">
              <span v-if="(sub.grade !== null || sub.booking || sub.is_failed_due_to_time) && revealedStudentIds.includes(sub.student_id)" class="text-[10px] font-bold print:text-sm print:font-black" :class="getRubricStats(sub).tech.ratio > 0 ? 'text-blue-600' : 'text-gray-400'">
                {{ getRubricStats(sub).tech.level }}
              </span>
              <span v-else class="text-gray-300 text-[10px]">—</span>
            </td>
            <td class="px-3 py-3 text-center">
              <span v-if="(sub.grade !== null || sub.booking || sub.is_failed_due_to_time) && revealedStudentIds.includes(sub.student_id)" class="text-[10px] font-bold print:text-sm print:font-black" :class="getRubricStats(sub).org.ratio > 0 ? 'text-amber-600' : 'text-gray-400'">
                {{ getRubricStats(sub).org.level }}
              </span>
              <span v-else class="text-gray-300 text-[10px]">—</span>
            </td>
            <td class="px-3 py-3 text-center">
              <span v-if="(sub.grade !== null || sub.booking || sub.is_failed_due_to_time) && revealedStudentIds.includes(sub.student_id)" class="text-[10px] font-bold print:text-sm print:font-black" :class="getRubricStats(sub).comp.ratio > 0 ? 'text-pink-600' : 'text-gray-400'">
                {{ getRubricStats(sub).comp.level }}
              </span>
              <span v-else class="text-gray-300 text-[10px]">—</span>
            </td>
            <td class="px-3 py-3 text-center">
              <span v-if="(sub.grade !== null || sub.booking || sub.is_failed_due_to_time) && revealedStudentIds.includes(sub.student_id)" class="text-[10px] font-bold print:text-sm print:font-black" :class="getRubricStats(sub).prof.ratio > 0 ? 'text-purple-600' : 'text-gray-400'">
                {{ getRubricStats(sub).prof.level }}
              </span>
              <span v-else class="text-gray-300 text-[10px]">—</span>
            </td>
            <td class="px-3 py-3 text-[11px] font-bold text-pink-500 print:text-base print:font-black">
              <span v-if="(sub.grade !== null || sub.status === 'submitted' || sub.status === 'graded' || sub.is_failed_due_to_time) && revealedStudentIds.includes(sub.student_id)" 
                :class="[(sub.grade === 0 || sub.is_failed_due_to_time) ? 'text-red-600' : 'text-pink-500', 'font-black print:text-base print:font-black']"
                :title="sub.grade === null ? 'Computed Preview Grade' : 'Final Grade'"
              >
                {{ getPercentage(sub) }}%
              </span>
              <span v-else class="text-gray-300 text-[10px]">—</span>
            </td>
            <td class="px-3 py-3 text-center print:hidden">
              <span v-if="sub.status === 'graded'" 
                :class="[
                  'px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-wider border',
                  (sub.is_failed_due_to_time || getPercentage(sub) < 60) 
                    ? 'bg-red-100 text-red-700 border-red-200' 
                    : 'bg-purple-100 text-purple-700 border-purple-200'
                ]">
                {{ (sub.is_failed_due_to_time || getPercentage(sub) < 60) ? 'FAIL' : 'PASS' }}
              </span>
              <span v-else :class="['px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-wider', getStatusClass(sub.status)]">
                {{ sub.status === 'submitted' ? 'SUB' : 'NOT' }}
              </span>
            </td>
            <td class="px-3 py-3 text-center print:hidden">
              <div v-if="sub.is_released" class="text-green-500 text-xs flex justify-center">✓</div>
              <div v-else-if="sub.grade !== null" class="text-amber-500 text-xs flex justify-center">○</div>
              <span v-else class="text-gray-300 text-[9px]">-</span>
            </td>
            <td class="px-3 py-3 print:hidden text-right">
              <button 
                v-if="sub.status === 'submitted' || sub.status === 'graded'"
                @click.stop="$emit('view-analysis', sub)"
                class="text-[8px] font-black text-pink-500 hover:text-pink-700 uppercase tracking-widest border border-pink-100 px-2 py-1 rounded hover:bg-pink-50 transition-all shadow-sm"
              >
                Details
              </button>
              <span v-else class="text-[8px] font-bold text-gray-300 uppercase tracking-widest px-2 py-1">Waiting</span>
            </td>
          </tr>
        </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div v-if="filteredStudentWork.length > pageSize" class="flex flex-col md:flex-row items-center justify-between mt-6 px-2 gap-4 print:hidden">
      <div class="flex items-center gap-4">
        <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest">Rows per page:</span>
        <select v-model="pageSize" class="bg-white border border-gray-200 rounded-lg px-2 py-1.5 text-[10px] font-black outline-none focus:ring-2 focus:ring-pink-500 transition-all cursor-pointer">
          <option :value="15">15</option>
          <option :value="30">30</option>
          <option :value="50">50</option>
        </select>
        <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
          Showing {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, filteredStudentWork.length) }} of {{ filteredStudentWork.length }}
        </span>
      </div>
      
      <div class="flex items-center gap-2">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="p-2.5 rounded-xl border border-gray-100 hover:bg-gray-50 disabled:opacity-20 disabled:hover:bg-transparent transition-all group"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-600 group-hover:text-pink-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <div class="flex items-center gap-1.5">
          <button 
            v-for="page in totalPages" 
            :key="page"
            @click="currentPage = page"
            :class="[
              'w-9 h-9 rounded-xl text-[10px] font-black transition-all flex items-center justify-center border',
              currentPage === page ? 'bg-pink-500 text-white border-pink-500 shadow-lg shadow-pink-200' : 'text-gray-400 border-transparent hover:bg-gray-50 hover:border-gray-100'
            ]"
          >
            {{ page }}
          </button>
        </div>
        
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="p-2.5 rounded-xl border border-gray-100 hover:bg-gray-50 disabled:opacity-20 disabled:hover:bg-transparent transition-all group"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-600 group-hover:text-pink-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { calculateLevel, calculateTotalGrade, calculatePercentage } from '@/utils/gradingLogic'

const props = defineProps({
  activity: Object,
  submissions: Array,
  submissions_loading: Boolean,
  releasing_grades: Boolean,
  is_printing: Boolean
})

const emit = defineEmits(['release-grades', 'print', 'refresh', 'view-analysis'])

const searchQuery = ref('')
const filterStatus = ref('all')
const currentPage = ref(1)
const pageSize = ref(15)

// --- Grade Visibility Logic ---
const revealedStudentIds = ref([])
const storageKey = computed(() => `fbs_revealed_grades_${props.activity?.id || 'default'}`)

// Load revealed students from localStorage when activity ID is available
watch(() => storageKey.value, (newKey) => {
    if (newKey !== 'fbs_revealed_grades_default') {
        try {
            const stored = localStorage.getItem(newKey)
            if (stored) revealedStudentIds.value = JSON.parse(stored)
        } catch(e) {}
    }
}, { immediate: true })

// Save revealed students back to localStorage when it changes
watch(() => revealedStudentIds.value, (newVal) => {
    try {
        if (storageKey.value !== 'fbs_revealed_grades_default') {
            localStorage.setItem(storageKey.value, JSON.stringify(newVal))
        }
    } catch(e) {}
}, { deep: true })

const hasHiddenGrades = computed(() => {
  return props.submissions.some(sub => 
    (sub.status === 'submitted' || sub.status === 'graded') && 
    !revealedStudentIds.value.includes(sub.student_id)
  )
})

const pendingHiddenCount = computed(() => {
  return props.submissions.filter(sub => 
    (sub.status === 'submitted' || sub.status === 'graded') && 
    !revealedStudentIds.value.includes(sub.student_id)
  ).length
})

const autoRevealPending = ref(false)

const revealGrades = () => {
    // 1. Immediately reveal any already-loaded submitted/graded students
    props.submissions.forEach(sub => {
        if (sub.status === 'submitted' || sub.status === 'graded' || sub.is_failed_due_to_time) {
            if (!revealedStudentIds.value.includes(sub.student_id)) {
                revealedStudentIds.value.push(sub.student_id)
            }
        }
    })
    // 2. Flag to auto-reveal after refresh, then trigger a server-side data refresh
    // This fetches the latest saved grades from the DB without visiting each student page
    autoRevealPending.value = true
    emit('refresh')
}

// Auto-reveal all submitted/graded students when fresh data comes in from server refresh
watch(() => props.submissions, (newSubs) => {
    if (!autoRevealPending.value) return
    newSubs.forEach(sub => {
        if ((sub.status === 'submitted' || sub.status === 'graded' || sub.is_failed_due_to_time) &&
            !revealedStudentIds.value.includes(sub.student_id)) {
            revealedStudentIds.value.push(sub.student_id)
        }
    })
    // Done — clear the auto-reveal flag
    autoRevealPending.value = false
}, { deep: true })
// -----------------------------

// True whenever ANY graded submission hasn't been released yet (to student dashboards)
// AND the instructor has already revealed it on their screen.
const hasUnreleasedGradedSubmissions = computed(() => {
  return props.submissions.some(sub =>
    (sub.grade !== null || sub.status === 'submitted' || sub.status === 'graded') &&
    revealedStudentIds.value.includes(sub.student_id) &&
    !sub.is_released
  )
})

const absoluteUnreleasedCount = computed(() => {
  return props.submissions.filter(sub =>
    (sub.grade !== null || sub.status === 'submitted' || sub.status === 'graded') &&
    !sub.is_released
  ).length
})

const pendingReleaseCount = computed(() => {
  return props.submissions.filter(sub =>
    (sub.grade !== null || sub.status === 'submitted' || sub.status === 'graded') &&
    revealedStudentIds.value.includes(sub.student_id) &&
    !sub.is_released
  ).length
})

const sortedSubmissions = computed(() => {
  return [...props.submissions].sort((a, b) => {
    if (a.grade === null && b.grade !== null) return 1
    if (a.grade !== null && b.grade === null) return -1
    if (a.grade === null && b.grade === null) return 0
    return b.grade - a.grade
  })
})

const topStudents = computed(() => {
  return sortedSubmissions.value.filter(s => s.grade !== null)
})

const totalStudents = computed(() => props.submissions.length)
const participationCount = computed(() => props.submissions.filter(s => s.booking !== null).length)
const passedCount = computed(() => props.submissions.filter(s => s.grade !== null && getPercentage(s) >= 60).length)

const classAverage = computed(() => {
  const graded = props.submissions.filter(s => s.grade !== null)
  if (graded.length === 0) return 0
  const totalPercentage = graded.reduce((sum, s) => sum + getPercentage(s), 0)
  return Math.round(totalPercentage / graded.length)
})

const passRate = computed(() => {
  if (totalStudents.value === 0) return 0
  return Math.round((passedCount.value / totalStudents.value) * 100)
})

const participationRate = computed(() => {
  if (totalStudents.value === 0) return 0
  return Math.round((participationCount.value / totalStudents.value) * 100)
})



const filteredStudentWork = computed(() => {
  let list = [...props.submissions]

  // Apply search
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(s =>
      s.first_name.toLowerCase().includes(q) ||
      s.last_name.toLowerCase().includes(q) ||
      (s.student_number || '').toLowerCase().includes(q)
    )
  }

  // Apply status filter
  if (filterStatus.value === 'passed') {
    list = list.filter(s => s.grade !== null && getPercentage(s) >= 60)
  } else if (filterStatus.value === 'failed') {
    list = list.filter(s => s.grade !== null && getPercentage(s) < 60)
  } else if (filterStatus.value === 'not taken') {
    list = list.filter(s => s.grade === null)
  }

  return list
})

const printChunks = computed(() => {
  const result = []
  const list = filteredStudentWork.value
  for (let i = 0; i < list.length; i += 15) {
    result.push(list.slice(i, i + 15))
  }
  return result
})

const paginatedStudentWork = computed(() => {
  // If printing, we show the entire filtered list
  if (props.is_printing) return filteredStudentWork.value
  
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredStudentWork.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(filteredStudentWork.value.length / pageSize.value))

// Reset pagination when search or filters change
watch([searchQuery, filterStatus, pageSize], () => {
  currentPage.value = 1
})

// getPercentage must match EXACTLY what instructor_students_score.vue shows as
// "Final Assessment Score". That view computes: sumOfRatios * (totalPoints/5)
// which equals (grade / totalPoints) * 100 when grade is set by the same formula.
// Using calculatePercentage from gradingLogic.js guarantees the same rounding.
const getPercentage = (sub) => {
  const totalPoints = parseFloat(props.activity?.total_points || 100)

  // Priority 1: Compute strictly from rubric_breakdown using live JS Math
  // This guarantees 100% parity with instructor_students_score final assessment display.
  let rb = sub.rubric_breakdown || [];
  if (typeof rb === 'string') { try { rb = JSON.parse(rb); } catch(e) { rb = []; } }
  if (Array.isArray(rb) && rb.length > 0) {
    const sumRatios = rb.reduce((sum, r) => sum + (r.ratio ?? 0), 0);
    const rawScore = sumRatios * (totalPoints / 5);
    return calculatePercentage(rawScore, totalPoints);
  }

  // Priority 2: Use the saved grade (set by backend grading service)
  if (sub.grade !== null && sub.grade !== undefined) {
    return calculatePercentage(parseFloat(sub.grade), totalPoints) // legacy DB fallback
  }

  // Priority 3: fall back to legacy analysis object
  if (sub.analysis) {
    const rawScore = calculateTotalGrade(sub.analysis, totalPoints)
    return calculatePercentage(rawScore, totalPoints)
  }

  return 0
}

const getRankWithSuffix = (rank) => {
  const j = rank % 10,
        k = rank % 100;
  if (j == 1 && k != 11) {
    return rank + "st";
  }
  if (j == 2 && k != 12) {
    return rank + "nd";
  }
  if (j == 3 && k != 13) {
    return rank + "rd";
  }
  return rank + "th";
}

const getStatusClass = (status) => {
  const classes = {
    'assigned': 'bg-gray-100 text-gray-600',
    'in_progress': 'bg-blue-100 text-blue-600',
    'submitted': 'bg-green-100 text-green-700',
    'graded': 'bg-purple-100 text-purple-700',
    'not_assigned': 'bg-red-50 text-red-400'
  }
  return classes[status] || 'bg-gray-50 text-gray-500'
}

const getRubricStats = (sub) => {
    let rb = sub.rubric_breakdown || [];
    if (typeof rb === 'string') {
        try { rb = JSON.parse(rb); } catch(e) { rb = []; }
    }
    const analysis = sub.analysis || {};
    
    if (sub.is_failed_due_to_time && sub.grade === null) {
        return {
            accuracy: { level: 1, ratio: 0, status: 'POOR' },
            tech: { level: 1, ratio: 0, status: 'POOR' },
            org: { level: 1, ratio: 0, status: 'POOR' },
            comp: { level: 1, ratio: 0, status: 'POOR' },
            prof: { level: 1, ratio: 0, status: 'POOR' },
            total: 0
        };
    }

    // Safely extract from instructor_student_score's rigorous breakdown data based on matching label keywords
    const getField = (keyword) => {
        // Priority 1: Exact mapping based on known labels from grading_service.py
        const mapping = {
            'accuracy': 'Accuracy',
            'tech': 'Technical',
            'org': 'Organization',
            'comp': 'Completeness',
            'prof': 'Professionalism'
        };
        const target = mapping[keyword];
        return rb.find(r => r.label && r.label.includes(target));
    };

    const accuracy = getField('accuracy') || (analysis.accuracy !== undefined ? { ...calculateLevel(analysis.accuracy, 'accuracy'), ratio: analysis.accuracy } : null);
    const tech = getField('tech') || (analysis.tech !== undefined ? { ...calculateLevel(analysis.tech, 'tech'), ratio: analysis.tech } : null);
    const org = getField('org') || (analysis.org !== undefined ? { ...calculateLevel(analysis.org, 'org'), ratio: analysis.org } : null);
    const comp = getField('comp') || (analysis.comp !== undefined ? { ...calculateLevel(analysis.comp, 'comp'), ratio: analysis.comp } : null);
    const prof = getField('prof') || (analysis.prof !== undefined ? { ...calculateLevel(analysis.prof, 'prof'), ratio: analysis.prof } : null);

    return {
        accuracy: { level: accuracy?.level || 1, ratio: accuracy?.ratio ?? 0, status: accuracy?.status || '—' },
        tech: { level: tech?.level || 1, ratio: tech?.ratio ?? 0, status: tech?.status || '—' },
        org: { level: org?.level || 1, ratio: org?.ratio ?? 0, status: org?.status || '—' },
        comp: { level: comp?.level || 1, ratio: comp?.ratio ?? 0, status: comp?.status || '—' },
        prof: { level: prof?.level || 1, ratio: prof?.ratio ?? 0, status: prof?.status || '—' },
        total: sub.grade !== null ? sub.grade : (analysis ? calculateTotalGrade(analysis, props.activity?.total_points) : 0)
    };
}

const formatTimeOnly = (t) => {
  if (!t) return ''
  const [h, m] = t.split(':')
  const hour = parseInt(h)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const h12 = hour % 12 || 12
  return `${h12}:${m} ${ampm}`
}

const formatSchedule = (scheduleData) => {
  if (!scheduleData) return 'No schedule set'
  try {
    const schedules = typeof scheduleData === 'string' ? JSON.parse(scheduleData) : scheduleData
    if (Array.isArray(schedules)) {
      if (schedules.length === 0) return 'No schedule set'
      return schedules.map(s => {
        const dayShort = s.day.substring(0, 3)
        return `${dayShort} ${formatTimeOnly(s.start_time)}-${formatTimeOnly(s.end_time)}`
      }).join(', ')
    }
  } catch (e) {}
  return scheduleData
}
</script>
