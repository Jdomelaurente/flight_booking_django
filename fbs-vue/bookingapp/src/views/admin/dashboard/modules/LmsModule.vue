<template>
  <div class="p-0.5 space-y-2">
    <!-- Loading Overlay -->
    <div v-if="loading" class="fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="flex flex-col items-center">
        <div class="w-12 h-12 border-4 border-[#fe3787] border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-gray-600 poppins">Syncing LMS Analytics...</p>
      </div>
    </div>

    <!-- Formal Print Header (Only visible when printing) -->
    <div class="hidden print:flex items-center justify-between mb-8 border-b-2 border-black pb-4">
      <div class="flex items-center gap-4">
        <div class="w-16 h-16 bg-[#fe3787] flex items-center justify-center text-white font-black text-2xl">LMS</div>
        <div>
          <h1 class="text-2xl font-black uppercase poppins">Academic Performance Report</h1>
          <p class="text-sm font-bold poppins text-gray-600 uppercase tracking-widest">School Management Division</p>
        </div>
      </div>
      <div class="text-right">
        <p class="text-xs font-black poppins uppercase">Report Generated:</p>
        <p class="text-xs font-medium poppins">{{ new Date().toLocaleString() }}</p>
      </div>
    </div>

    <!-- Basic Header -->
    <div class="relative overflow-hidden p-3 rounded-[1px] border border-white/20 shadow-2xl bg-gradient-to-br from-[#002D1E] to-[#013d29] mb-2 group no-print">
      <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
      <div class="absolute -right-20 -top-20 w-64 h-64 bg-[#fe3787] rounded-full blur-[100px] opacity-20 group-hover:opacity-30 transition-opacity"></div>
      
      <div class="relative flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/10 mb-4">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span class="text-[9px] font-bold text-white uppercase tracking-widest poppins">School Information</span>
          </div>
          <h1 class="text-xl font-black text-white poppins tracking-tight mb-2">
            School <span class="text-[#fe3787] drop-shadow-sm font-black italic">Stats</span>
          </h1>
          <p class="text-gray-300 poppins text-sm max-w-md">Track your classrooms, student grades, and teacher work here.</p>
        </div>
        
        <div class="flex items-center gap-4">
          <!-- Generate Report Button -->
          <button 
            @click="printReport"
            class="hidden md:flex items-center gap-2 px-5 py-2.5 bg-white text-[#002D1E] rounded-[1px] font-black uppercase text-[10px] tracking-widest poppins hover:bg-emerald-50 transition-all shadow-xl group/btn"
          >
            <i class="ph ph-printer text-lg group-hover/btn:scale-110 transition-transform"></i>
            Generate Report
          </button>

          <div class="flex items-center gap-3 bg-black/20 backdrop-blur-xl p-3 rounded-[1px] border border-white/10 shadow-inner">
            <div class="w-12 h-12 rounded-[1px] bg-[#fe3787] flex items-center justify-center shadow-lg">
              <i class="ph ph-student text-white text-2xl"></i>
            </div>
            <div>
              <p class="text-[10px] uppercase font-bold text-gray-400 tracking-widest poppins mb-1">Total Students</p>
              <p class="text-sm font-black text-white poppins leading-none">{{ totals.students }} Students</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Metric Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 mb-2 no-print">
      <!-- Active Classrooms -->
      <div class="group bg-white p-2.5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden text-[#002D1E]">
        <div class="absolute top-0 right-0 w-24 h-24 bg-blue-50/50 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-500 tracking-[0.2em] poppins">Classrooms</p>
            <p class="text-xl font-black poppins mt-1 tracking-tighter">{{ totals.sections }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-blue-50 flex items-center justify-center border border-blue-100 shadow-inner">
            <i class="ph ph-chalkboard-simple text-blue-600 text-xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-4 flex items-center text-[9px] font-black uppercase text-gray-400 tracking-widest">
           {{ totals.instructors }} Teachers
        </div>
      </div>

      <!-- Activity Vault -->
      <div class="group bg-white p-2.5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden text-[#002D1E]">
        <div class="absolute top-0 right-0 w-24 h-24 bg-pink-50/50 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-500 tracking-[0.2em] poppins">Lessons</p>
            <p class="text-xl font-black poppins mt-1 tracking-tighter">{{ totals.activities }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-pink-50 flex items-center justify-center border border-pink-100 shadow-inner">
            <i class="ph ph-books text-[#fe3787] text-xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-4 flex items-center text-[9px] font-black uppercase text-gray-400 tracking-widest">
           {{ totals.bindings }} Homeworks
        </div>
      </div>

      <!-- Grading Progress -->
      <div class="group bg-white p-2.5 border border-gray-200 rounded-[1px] shadow-sm hover:shadow-xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden text-[#002D1E]">
        <div class="relative flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-500 tracking-[0.2em] poppins">Finished Work</p>
            <p class="text-xl font-black poppins mt-1 tracking-tighter">{{ completionPercentage }}%</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-emerald-50 flex items-center justify-center border border-emerald-100 shadow-inner">
            <i class="ph ph-check-square-offset text-emerald-600 text-xl transition-transform group-hover:rotate-12"></i>
          </div>
        </div>
        <div class="mt-4 w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
           <div class="bg-emerald-500 h-full transition-all duration-1000" :style="{ width: completionPercentage + '%' }"></div>
        </div>
      </div>

      <!-- Average Rating -->
      <div class="group bg-[#002D1E] p-2.5 border border-[#002D1E] rounded-[1px] shadow-sm hover:shadow-2xl transition-all hover:-translate-y-1 duration-300 relative overflow-hidden text-white">
        <div class="absolute top-0 right-0 w-24 h-24 bg-[#fe3787]/10 rounded-full -mr-12 -mt-12 transition-transform group-hover:scale-110"></div>
        <div class="relative flex items-center justify-between">
          <div>
            <p class="text-[10px] uppercase font-bold text-gray-400 tracking-[0.2em] poppins">Average Grade</p>
            <p class="text-xl font-black text-[#fe3787] poppins mt-1 tracking-tighter">{{ averageGrade }}</p>
          </div>
          <div class="w-14 h-14 rounded-[1px] bg-white/5 flex items-center justify-center border border-white/10 shadow-inner backdrop-blur-sm">
            <i class="ph ph-star-four text-[#fe3787] text-xl"></i>
          </div>
        </div>
        <div class="mt-4 flex items-center text-[9px] font-black uppercase text-gray-500 tracking-widest">
           School Average
        </div>
      </div>
    </div>

    <!-- Trends Section -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-2 mb-2">
       <!-- Student Work Trends -->
       <div class="lg:col-span-8 bg-white border border-gray-200 p-4 rounded-[1px] shadow-sm relative group h-[380px] flex flex-col student-trends-section">
          <div class="absolute top-0 right-0 w-24 h-24 bg-blue-50/50 rounded-full blur-[40px] pointer-events-none group-hover:bg-blue-100/50 transition-all"></div>
          <div class="flex items-center justify-between mb-8 relative">
            <div class="flex items-center gap-3">
               <div class="w-2 h-8 bg-blue-600 rounded-[1px] shadow-[0_0_10px_rgba(37,99,235,0.2)]"></div>
               <div>
                                   <h2 class="hidden print:block text-2xl font-black uppercase mb-4 text-[#002D1E] poppins border-b-2 border-[#002D1E] pb-2">PAGE 1: ACADEMIC TRENDS</h2>
                  <h3 class="text-xs font-black text-[#002D1E] poppins uppercase tracking-widest">Student Work Trends</h3>
                 <p class="text-[9px] text-gray-400 font-bold poppins uppercase">Submissions this month</p>
               </div>
            </div>
            <!-- Period Selector -->
            <div class="flex items-center bg-gray-50 border border-gray-100 p-0.5 rounded-[1px] relative z-20 no-print">
               <button 
                 v-for="p in ['weekly', 'monthly', 'yearly']" 
                 :key="p"
                 @click="timelinePeriod = p"
                 :class="timelinePeriod === p ? 'bg-[#002D1E] text-white shadow-lg' : 'text-gray-400 hover:text-gray-600'"
                 class="px-3 py-1 text-[8px] font-black uppercase poppins rounded-[1px] transition-all"
               >
                 {{ p }}
               </button>
            </div>
          </div>
        <div class="h-[240px] relative">
          <canvas ref="timelineChartRef"></canvas>
          <div v-if="timeline.length === 0 && !loading" class="absolute inset-0 flex flex-col items-center justify-center bg-white/50">
             <i class="ph ph-chart-line text-4xl text-gray-200 mb-2"></i>
             <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">No work recorded yet</p>
          </div>
        </div>
      </div>

      <!-- Activity Progress -->
      <div class="lg:col-span-4 bg-white p-3 border border-gray-200 rounded-[1px] shadow-sm flex flex-col relative group overflow-hidden homework-status-section">
                     <h2 class="hidden print:block text-2xl font-black uppercase mb-4 text-[#002D1E] poppins border-b-2 border-[#002D1E] pb-2">PAGE 2: TASK COMPLETION STATUS</h2>
           <h3 class="text-[10px] font-black text-[#002D1E] poppins uppercase tracking-widest mb-6 relative px-1">Homework Status</h3>
          <div class="flex-grow flex items-center justify-center min-h-[180px] relative">
            <canvas ref="statusChartRef"></canvas>
            <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none translate-y-[-10px]">
              <span class="text-2xl font-black text-[#002D1E] poppins">{{ totals.bindings }}</span>
              <span class="text-[8px] font-bold text-gray-400 uppercase tracking-widest poppins">Tasks</span>
            </div>
          </div>
          <div class="mt-4 space-y-1.5 relative p-1">
             <div v-for="(count, status) in statusBreakdown" :key="status" class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                   <span class="w-2 h-2 rounded-[1px]" :class="statusColorClass(status)"></span>
                   <span class="text-[9px] font-black text-gray-500 uppercase poppins">{{ status.replace('_', ' ') }}</span>
                </div>
                <span class="text-[9px] font-black text-[#002D1E] poppins">{{ count }}</span>
             </div>
          </div>
      </div>
    </div>

       <!-- Top Classes & Students -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-2 mb-2 classroom-progress-section">
       <!-- Classroom Progress -->
       <div class="lg:col-span-7 bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden flex flex-col min-h-[400px]">
          <h2 class="hidden print:block text-2xl font-black uppercase p-4 text-[#002D1E] poppins border-b-2 border-[#002D1E] mb-2">PAGE 3: CLASSROOM PROGRESS REPORT</h2>
          <div class="p-4 border-b border-gray-200 flex items-center justify-between bg-gray-50/30">
            <h3 class="text-xs font-black text-[#002D1E] poppins uppercase tracking-widest flex items-center gap-2">
              <i class="ph ph-users-four text-blue-600"></i>
              Classroom Progress
            </h3>
            <span class="text-[9px] font-black bg-blue-50 text-blue-600 px-2 py-0.5 rounded-[1px]">{{ sectionStats.length }} Active</span>
          </div>
          <div class="flex-grow">
            <table class="w-full text-left border-collapse">
              <thead class="bg-gray-50 text-gray-400 text-[9px] uppercase font-black tracking-widest border-b border-gray-100">
                <tr>
                  <th class="px-5 py-3 poppins">Class Name</th>
                  <th class="px-5 py-3 poppins text-center">Students</th>
                  <th class="px-5 py-3 poppins text-center">Progress</th>
                  <th class="px-5 py-3 poppins text-right">Avg Grade</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="sec in paginatedSections" :key="sec.name" class="hover:bg-gray-50/50 transition-colors">
                  <td class="px-5 py-3">
                     <p class="text-[10px] font-black text-[#002D1E] poppins uppercase tracking-tight">{{ sec.name }}</p>
                  </td>
                  <td class="px-5 py-3 text-center">
                     <span class="text-[10px] font-bold text-gray-500">{{ sec.enrolled }}</span>
                  </td>
                  <td class="px-5 py-3">
                     <div class="flex items-center justify-center gap-3">
                        <div class="w-16 bg-gray-100 h-1 rounded-full overflow-hidden">
                           <div class="bg-emerald-500 h-full" :style="{ width: sec.rate + '%' }"></div>
                        </div>
                        <span class="text-[9px] font-black text-emerald-600">{{ sec.rate }}%</span>
                     </div>
                  </td>
                  <td class="px-5 py-3 text-right">
                     <span class="text-[10px] font-black text-[#fe3787]">{{ sec.avg_grade || '0.0' }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- Pagination -->
          <div class="p-3 border-t border-gray-100 flex items-center justify-between bg-gray-50/20 no-print">
             <span class="text-[8px] font-black text-gray-400 uppercase tracking-widest">Page {{ sectionPage }} of {{ sectionTotalPages }}</span>
             <div class="flex items-center gap-2">
                <button @click="sectionPage--" :disabled="sectionPage === 1" class="w-6 h-6 flex items-center justify-center border border-gray-200 text-gray-400 hover:text-blue-600 disabled:opacity-20 transition-all bg-white"><i class="ph ph-caret-left"></i></button>
                <button @click="sectionPage++" :disabled="sectionPage >= sectionTotalPages" class="w-6 h-6 flex items-center justify-center border border-gray-200 text-gray-400 hover:text-blue-600 disabled:opacity-20 transition-all bg-white"><i class="ph ph-caret-right"></i></button>
             </div>
          </div>
       </div>

        <!-- Student Lists (Unified) -->
        <div class="lg:col-span-5 bg-[#002D1E] rounded-[1px] shadow-lg border border-[#002D1E] overflow-hidden flex flex-col text-white min-h-[440px] student-lists-section">
           <div class="p-4 border-b border-white/10 flex items-center justify-between bg-black/10">
             <div class="flex items-center gap-4">
                <button @click="studentBoardTab = 'top'" 
                        :class="studentBoardTab === 'top' ? 'text-white border-b-2 border-[#fe3787]' : 'text-gray-500 hover:text-gray-300'"
                        class="text-[10px] font-black poppins uppercase tracking-widest pb-1 transition-all">
                  Top Students
                </button>
                <button @click="studentBoardTab = 'risk'" 
                        :class="studentBoardTab === 'risk' ? 'text-white border-b-2 border-rose-500' : 'text-gray-500 hover:text-gray-300'"
                        class="text-[10px] font-black poppins uppercase tracking-widest pb-1 transition-all">
                  Needs Help
                </button>
             </div>
             <div class="flex items-center gap-2">
                <i :class="studentBoardTab === 'top' ? 'ph ph-crown text-yellow-400' : 'ph ph-warning-diamond text-rose-500'" class="text-xl"></i>
             </div>
           </div>

           <!-- Top Achievers View -->
           <div v-if="studentBoardTab === 'top'" class="p-2 space-y-1 flex-grow overflow-y-auto">
              <div v-for="(student, idx) in paginatedStudents" :key="student.student_number" 
                   class="flex items-center justify-between p-2 rounded-[1px] border border-white/5 hover:bg-white/5 transition-all group">
                 <div class="flex items-center gap-3">
                    <div class="w-7 h-7 flex items-center justify-center rounded-[1px] text-[10px] font-black"
                         :class="studentRank(student.student_number) < 3 ? 'bg-[#fe3787] text-white' : 'bg-white/10 text-gray-400'">
                       0{{ studentRank(student.student_number) + 1 }}
                    </div>
                    <div>
                       <p class="text-[10px] font-black uppercase poppins">{{ student.name }}</p>
                       <p class="text-[8px] text-gray-500 tracking-widest uppercase font-bold">{{ student.student_number }}</p>
                    </div>
                 </div>
                 <div class="text-right">
                    <p class="text-[11px] font-black text-[#fe3787] poppins">{{ student.avg_grade }}</p>
                    <p class="text-[8px] text-emerald-400 font-bold uppercase">{{ student.completed }} DONE</p>
                 </div>
              </div>
              <!-- Pagination for Top Students -->
              <div class="p-3 border-t border-white/10 flex items-center justify-between bg-black/10 mt-auto">
                 <span class="text-[8px] font-black text-gray-500 uppercase tracking-widest">Page {{ studentPage }} / {{ studentTotalPages }}</span>
                 <div class="flex items-center gap-2">
                    <button @click="studentPage--" :disabled="studentPage === 1" class="w-5 h-5 flex items-center justify-center border border-white/10 text-gray-400 hover:text-[#fe3787] disabled:opacity-20 transition-all"><i class="ph ph-caret-left text-xs"></i></button>
                    <button @click="studentPage++" :disabled="studentPage >= studentTotalPages" class="w-5 h-5 flex items-center justify-center border border-white/10 text-gray-400 hover:text-[#fe3787] disabled:opacity-20 transition-all"><i class="ph ph-caret-right text-xs"></i></button>
                 </div>
              </div>
           </div>

           <!-- Risk Analysis View -->
           <div v-if="studentBoardTab === 'risk'" class="p-2 space-y-1 flex-grow overflow-y-auto">
              <div v-for="student in paginatedRisk" :key="student.student_number" 
                   class="flex items-center justify-between p-2 rounded-[1px] border border-white/5 hover:bg-rose-500/10 transition-all group">
                 <div class="flex items-center gap-3">
                    <div class="w-7 h-7 flex items-center justify-center rounded-[1px] text-[10px] font-black bg-rose-500/20 text-rose-500">
                       <i class="ph ph-warning"></i>
                    </div>
                    <div>
                       <p class="text-[10px] font-black uppercase poppins">{{ student.name }}</p>
                       <p class="text-[8px] text-rose-400 font-bold uppercase tracking-widest">{{ student.reason }}</p>
                    </div>
                 </div>
                 <div class="text-right">
                    <p class="text-[11px] font-black text-rose-500 poppins">{{ student.avg_grade }}</p>
                    <p class="text-[8px] text-gray-500 font-bold uppercase">{{ student.missing }} MISSED</p>
                 </div>
              </div>
              <div v-if="atRiskStudents.length === 0" class="flex flex-col items-center justify-center h-48 text-gray-600">
                 <i class="ph ph-shield-check text-4xl mb-2 opacity-20"></i>
                 <p class="text-[9px] font-black uppercase tracking-widest">No Risk Detected</p>
              </div>
              <!-- Pagination for Risk -->
              <div v-if="atRiskStudents.length > 0" class="p-3 border-t border-white/10 flex items-center justify-between bg-black/10 mt-auto">
                 <span class="text-[8px] font-black text-gray-500 uppercase tracking-widest">Page {{ riskPage }} / {{ riskTotalPages }}</span>
                 <div class="flex items-center gap-2">
                    <button @click="riskPage--" :disabled="riskPage === 1" class="w-5 h-5 flex items-center justify-center border border-white/10 text-gray-400 hover:text-rose-500 disabled:opacity-20 transition-all"><i class="ph ph-caret-left text-xs"></i></button>
                    <button @click="riskPage++" :disabled="riskPage >= riskTotalPages" class="w-5 h-5 flex items-center justify-center border border-white/10 text-gray-400 hover:text-rose-500 disabled:opacity-20 transition-all"><i class="ph ph-caret-right text-xs"></i></button>
                 </div>
              </div>
           </div>
        </div>
     </div>

     <!-- Teacher Performance (Managerial) -->
      <div>
        <h2 class="hidden print:block text-xl font-black uppercase mb-4">PAGE 4: TEACHER PERFORMANCE</h2>
        <div class="bg-white border border-gray-200 rounded-[1px] shadow-sm overflow-hidden flex flex-col mb-2 relative group teacher-work-section">
        <div class="absolute inset-0 bg-blue-50/5 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="p-4 border-b border-gray-100 flex items-center justify-between bg-white relative">
           <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-[1px] bg-blue-50 flex items-center justify-center border border-blue-100">
                 <i class="ph ph-briefcase text-blue-600 text-xl"></i>
              </div>
              <div>
                 <h3 class="text-xs font-black text-[#002D1E] poppins uppercase tracking-widest">Teacher Work</h3>
                 <p class="text-[9px] text-gray-400 font-bold poppins uppercase">Instructor workload and grading health</p>
              </div>
           </div>
           <span class="text-[9px] font-black text-blue-600 bg-blue-50 px-3 py-1 rounded-[1px] border border-blue-100">{{ teacherStats.length }} TOTAL TEACHERS</span>
        </div>
        <div class="relative overflow-x-auto">
           <table class="w-full text-left">
             <thead class="bg-gray-50/80 text-[9px] font-black text-gray-500 uppercase border-b border-gray-100">
                <tr>
                   <th class="px-6 py-2.5">Instructor Name</th>
                   <th class="px-6 py-2.5">Classrooms</th>
                   <th class="px-6 py-2.5">Students Handled</th>
                   <th class="px-6 py-2.5">Work Progress</th>
                   <th class="px-6 py-2.5 text-right">Activity Score</th>
                </tr>
             </thead>
             <tbody class="divide-y divide-gray-50">
                <tr v-for="teacher in paginatedTeachers" :key="teacher.name" class="hover:bg-blue-50/30 transition-colors">
                   <td class="px-6 py-3">
                      <div class="flex items-center gap-3">
                         <div class="w-8 h-8 rounded-full bg-blue-600 border border-blue-700 flex items-center justify-center text-[10px] font-bold text-white poppins">
                            {{ teacher.name.charAt(0) }}
                         </div>
                         <p class="text-[10px] font-black text-[#002D1E] poppins uppercase">{{ teacher.name }}</p>
                      </div>
                   </td>
                   <td class="px-6 py-3">
                      <span class="text-[10px] font-black text-gray-600">{{ teacher.sections }} Sections</span>
                   </td>
                   <td class="px-6 py-3">
                      <span class="text-[10px] font-black text-gray-600">{{ teacher.students }} Students</span>
                   </td>
                   <td class="px-6 py-3">
                      <div class="flex items-center gap-2">
                         <div class="w-20 bg-gray-100 h-1 rounded-full overflow-hidden">
                            <div class="h-full bg-blue-500" :style="{ width: teacher.rate + '%' }"></div>
                         </div>
                         <span class="text-[9px] font-black text-blue-600">{{ teacher.rate }}%</span>
                      </div>
                   </td>
                   <td class="px-6 py-3 text-right">
                      <span class="text-[10px] font-black" :class="teacher.rate > 80 ? 'text-emerald-500' : 'text-gray-400'">
                         {{ teacher.tasks }} Tasks Given
                      </span>
                   </td>
                </tr>
                <tr v-if="teacherStats.length === 0">
                   <td colspan="5" class="px-6 py-12 text-center text-gray-300">
                      <i class="ph ph-user-list text-4xl mb-2 block"></i>
                      <p class="text-[10px] font-black uppercase tracking-[0.3em]">No instructor data found</p>
                   </td>
                </tr>
             </tbody>
           </table>
        </div>
        <!-- Pagination for Teacher -->
        <div v-if="teacherStats.length > 0" class="p-3 border-t border-gray-100 flex items-center justify-between bg-gray-50/20 no-print">
             <span class="text-[8px] font-black text-gray-400 uppercase tracking-widest">Page {{ teacherPage }} of {{ teacherTotalPages }}</span>
             <div class="flex items-center gap-2">
                <button @click="teacherPage--" :disabled="teacherPage === 1" class="w-6 h-6 flex items-center justify-center border border-gray-200 text-gray-400 hover:text-blue-600 disabled:opacity-20 transition-all bg-white"><i class="ph ph-caret-left"></i></button>
                <button @click="teacherPage++" :disabled="teacherPage >= teacherTotalPages" class="w-6 h-6 flex items-center justify-center border border-gray-200 text-gray-400 hover:text-blue-600 disabled:opacity-20 transition-all bg-white"><i class="ph ph-caret-right"></i></button>
             </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, nextTick, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '@/services/admin/api'

Chart.register(...registerables)

const loading = ref(false)

// Data State
const totals = ref({
  students: 0,
  instructors: 0,
  sections: 0,
  activities: 0,
  bindings: 0
})
const statusBreakdown = ref({})
const sectionStats = ref([])
const timeline = ref([])
const topStudents = ref([])
const atRiskStudents = ref([])
const teacherStats = ref([])
const studentBoardTab = ref('top')
const timelinePeriod = ref('weekly')

watch(timelinePeriod, () => {
  fetchTimelineData()
})

const fetchTimelineData = async () => {
  try {
    const res = await api.get(`/admin/lms-overview/?period=${timelinePeriod.value}`)
    timeline.value = res.data.timeline || []
    await nextTick()
    initTimelineChart()
  } catch (err) {
    console.error('Failed to fetch filtered timeline:', err)
  }
}

// Pagination State
const sectionPage = ref(1)
const sectionPageSize = ref(5)
const sectionTotalPages = computed(() => Math.ceil(sectionStats.value.length / sectionPageSize.value))
const paginatedSections = computed(() => {
  const start = (sectionPage.value - 1) * sectionPageSize.value
  return sectionStats.value.slice(start, start + sectionPageSize.value)
})

const studentPage = ref(1)
const studentPageSize = ref(6)
const studentTotalPages = computed(() => Math.ceil(topStudents.value.length / studentPageSize.value))
const paginatedStudents = computed(() => {
  const start = (studentPage.value - 1) * studentPageSize.value
  return topStudents.value.slice(start, start + studentPageSize.value)
})

const riskPage = ref(1)
const riskPageSize = ref(5)
const riskTotalPages = computed(() => Math.ceil(atRiskStudents.value.length / riskPageSize.value))
const paginatedRisk = computed(() => {
  const start = (riskPage.value - 1) * riskPageSize.value
  return atRiskStudents.value.slice(start, start + riskPageSize.value)
})

const teacherPage = ref(1)
const teacherPageSize = ref(5)
const teacherTotalPages = computed(() => Math.ceil(teacherStats.value.length / teacherPageSize.value))
const paginatedTeachers = computed(() => {
  const start = (teacherPage.value - 1) * teacherPageSize.value
  return teacherStats.value.slice(start, start + teacherPageSize.value)
})

const studentRank = (studentNumber) => {
  return topStudents.value.findIndex(s => s.student_number === studentNumber)
}

// Chart Refs
const timelineChartRef = ref(null)
const statusChartRef = ref(null)

let timelineChartInstance = null
let statusChartInstance = null

// Computed
const completionPercentage = computed(() => {
  if (!totals.value.bindings) return 0
  const completed = statusBreakdown.value['completed'] || 0
  const submitted = statusBreakdown.value['submitted'] || 0
  const graded = statusBreakdown.value['graded'] || 0
  return Math.round(((completed + submitted + graded) / totals.value.bindings) * 100)
})

const averageGrade = computed(() => {
  if (topStudents.value.length === 0) return '0.0'
  const sum = topStudents.value.reduce((acc, curr) => acc + curr.avg_grade, 0)
  return (sum / topStudents.value.length).toFixed(1)
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await api.get(`/admin/lms-overview/?period=${timelinePeriod.value}`)
    const d = res.data
    
    totals.value = d.totals || totals.value
    statusBreakdown.value = d.status_breakdown || {}
    sectionStats.value = d.section_stats || []
    timeline.value = d.timeline || []
    topStudents.value = d.top_students || []
    atRiskStudents.value = d.at_risk_students || []
    teacherStats.value = d.teacher_stats || []

    await nextTick()
    initCharts()
  } catch (err) {
    console.error('LMS Overview Fetch Error:', err)
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  initTimelineChart()
  initStatusChart()
}

const initTimelineChart = () => {
  if (!timelineChartRef.value) return
  if (timelineChartInstance) timelineChartInstance.destroy()
  
  const ctx = timelineChartRef.value.getContext('2d')
  const gradient = ctx.createLinearGradient(0, 0, 0, 400)
  gradient.addColorStop(0, 'rgba(254, 55, 135, 0.1)')
  gradient.addColorStop(1, 'rgba(254, 55, 135, 0)')

  timelineChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: timeline.value.map(i => i.week),
      datasets: [{
        label: 'Submissions',
        data: timeline.value.map(i => i.count),
        borderColor: '#fe3787',
        borderWidth: 3,
        backgroundColor: gradient,
        tension: 0.4,
        fill: true,
        pointRadius: 4,
        pointBackgroundColor: '#fe3787',
        pointBorderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: '#f3f4f6' }, ticks: { font: { size: 9, family: 'Poppins' } } },
        x: { grid: { display: false }, ticks: { font: { size: 9, family: 'Poppins' } } }
      }
    }
  })
}

const initStatusChart = () => {
  if (!statusChartRef.value) return
  if (statusChartInstance) statusChartInstance.destroy()
  
  const labels = Object.keys(statusBreakdown.value)
  const data = Object.values(statusBreakdown.value)
  const colors = labels.map(l => {
    if (l === 'completed') return '#10b981'
    if (l === 'submitted') return '#3b82f6'
    if (l === 'in_progress') return '#f59e0b'
    if (l === 'assigned') return '#94a3b8'
    if (l === 'graded') return '#6366f1'
    return '#fe3787'
  })

  statusChartInstance = new Chart(statusChartRef.value, {
    type: 'doughnut',
    data: {
      labels: labels.map(l => l.toUpperCase()),
      datasets: [{
        data: data.length ? data : [1],
        backgroundColor: data.length ? colors : ['#f3f4f6'],
        borderWidth: 5,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: '82%',
      plugins: { legend: { display: false } }
    }
  })
}

const statusColorClass = (status) => {
  const map = {
    'completed': 'bg-emerald-500',
    'submitted': 'bg-blue-500',
    'in_progress': 'bg-amber-500',
    'assigned': 'bg-gray-400',
    'graded': 'bg-indigo-500'
  }
  return map[status] || 'bg-pink-500'
}

const printReport = () => {
  window.print()
}

onMounted(fetchData)
onUnmounted(() => {
  [timelineChartInstance, statusChartInstance].forEach(i => i?.destroy())
})
</script>

<style scoped>
.poppins { font-family: 'Poppins', sans-serif; }
@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 1s linear infinite; }

@media print {
  .no-print, 
  button, 
  .period-selector,
  .ph,
  header,
  nav,
  aside,
  .sticky {
    display: none !important;
  }

  body {
    background: white !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  /* Force colors and gradients to print */
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  /* 4-Page Integrated Report Concept */
  .grid {
    display: block !important;
  }

  .lg\:col-span-8, .lg\:col-span-4, .lg\:col-span-7, .lg\:col-span-5 {
    width: 100% !important;
    margin-bottom: 0 !important;
  }

  /* Dynamic Page Breaks - PREVENT BLANK PAGES */
  .student-trends-section {
    page-break-after: always !important;
    break-after: page !important;
    margin-bottom: 0 !important;
  }

  .homework-status-section,
  .classroom-progress-section,
  .teacher-work-section {
    page-break-before: always !important;
    break-before: page !important;
    margin-bottom: 0 !important;
    padding-top: 20px !important;
  }

  /* Force only the 4 main sections to show and prevent trailing blanks */
  .no-print {
    display: none !important;
  }

  .mb-2 {
    margin-bottom: 0 !important;
  }

  canvas {
    max-width: 100% !important;
    height: 420px !important; 
  }

  .shadow-sm, .shadow-xl {
    box-shadow: none !important;
    border: 1px solid #eee !important;
  }
}
</style>
