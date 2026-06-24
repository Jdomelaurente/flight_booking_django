<template>
  <div class="p-4 lg:p-8 max-w-7xl mx-auto">
    <!-- Welcome and Breadcrumbs -->
    <div class="mb-2">
      <h2 class="text-xl font-bold text-slate-800 tracking-tight">Instructor Dashboard</h2>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
      <div class="bg-white p-4 rounded-md shadow-sm flex items-center gap-3 transition-all hover:shadow-md">
        <div class="w-10 h-10 bg-pink-50 rounded-md flex items-center justify-center text-pink-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Total Sections</p>
          <h4 class="text-xl font-bold text-slate-700">{{ sections?.length || 0 }}</h4>
        </div>
      </div>

      <div class="bg-white p-4 rounded-md shadow-sm flex items-center gap-3 transition-all hover:shadow-md">
        <div class="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center text-emerald-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Total Students</p>
          <h4 class="text-xl font-bold text-slate-700">{{ totalStudents }}</h4>
        </div>
      </div>

      <div class="bg-white p-4 rounded-md shadow-sm flex items-center gap-3 transition-all hover:shadow-md">
        <div class="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-blue-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Active Activities</p>
          <h4 class="text-xl font-bold text-slate-700">{{ totalActivities }}</h4>
        </div>
      </div>

      <div class="bg-white p-4 rounded-md shadow-sm flex items-center gap-3 transition-all hover:shadow-md">
        <div class="w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center text-amber-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-tight">Last Update</p>
          <h4 class="text-sm font-bold text-slate-700">{{ lastSyncTime }}</h4>
        </div>
      </div>
    </div>

    <!-- Section Controls -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
      <h3 class="text-lg font-bold text-slate-700">Academic Sections</h3>
      
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <div class="relative flex-1 sm:w-64">
          <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search sections..." 
            class="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-pink-500/20 focus:border-pink-500 transition-all shadow-sm"
          >
        </div>
        <button 
          @click="showModal = true"
          class="bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 shadow-sm transition-all active:scale-95 whitespace-nowrap"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Register New
        </button>
      </div>
    </div>

    <!-- Grid View -->
    <div v-if="!searchQuery || filteredSections.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
      <!-- Register New Section Card -->
      <div 
        v-if="!searchQuery"
        @click="showModal = true"
        class="group border-2 border-dashed border-slate-200 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer hover:border-pink-500 hover:bg-pink-50 transition-all duration-300 min-h-[260px] bg-white shadow-sm hover:shadow-md"
      >
        <div class="w-16 h-16 bg-slate-50 border-2 border-dashed border-slate-200 rounded-full flex items-center justify-center mb-4 group-hover:border-pink-500 group-hover:bg-white transition-all duration-300">
          <span class="text-3xl text-slate-300 group-hover:text-pink-500 transition-colors">+</span>
        </div>
        <p class="text-slate-500 font-bold uppercase text-xs tracking-widest group-hover:text-pink-600 transition-colors text-center">Register New Section</p>
      </div>

      <div 
        v-for="section in filteredSections" 
        :key="section.id" 
        @click="goToSection(section.id)" 
        class="group bg-white rounded-2xl shadow-sm hover:shadow-md border border-slate-200 hover:border-pink-200 overflow-hidden transition-all duration-300 cursor-pointer flex flex-col h-full relative"
      >
        <!-- Top accent line -->
        <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-pink-500 to-pink-400 opacity-0 group-hover:opacity-100 transition-opacity"></div>

        <div class="p-5 sm:p-6 flex-1 flex flex-col">
          <div class="flex justify-between items-start mb-5">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-xl bg-pink-50 flex items-center justify-center font-bold text-lg text-pink-600 border border-pink-100 flex-shrink-0">
                {{ section.section_name.charAt(0) }}
              </div>
              <div>
                <span class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-400 block mb-1">{{ section.section_code }}</span>
                <h3 class="text-base font-bold text-slate-800 leading-tight group-hover:text-pink-600 transition-colors">{{ section.section_name }}</h3>
              </div>
            </div>
            
            <div class="flex items-center gap-1.5">
              <span v-if="!section.is_active" class="bg-red-50 text-red-500 text-[9px] px-2 py-0.5 rounded-md border border-red-100 font-bold uppercase tracking-wider">Inactive</span>
              <button @click.stop="editSection(section)" class="p-1.5 text-slate-300 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
          </div>

          <div class="mb-5">
             <p class="text-[13px] text-slate-500 leading-relaxed line-clamp-2 pr-2">
               {{ section.description || 'Provide a detailed overview of this section to help organize your curriculum.' }}
             </p>
          </div>
          
          <div v-if="section.schedule" class="flex flex-wrap gap-2 mt-auto pt-2">
            <template v-if="Array.isArray(parsedSectionSchedule(section.schedule))">
               <span v-for="(s, i) in parsedSectionSchedule(section.schedule).slice(0, 3)" :key="i" class="text-[9px] bg-slate-50 text-slate-500 px-2 py-1 rounded-md border border-slate-100 font-bold uppercase tracking-widest flex items-center gap-1.5">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                 </svg>
                 {{ s.day.substring(0, 3) }} {{ formatTimeOnly(s.start_time) }}
               </span>
               <span v-if="parsedSectionSchedule(section.schedule).length > 3" class="text-[9px] text-slate-400 self-center font-bold ml-1">+{{ parsedSectionSchedule(section.schedule).length - 3 }}</span>
            </template>
            <span v-else class="text-[9px] bg-slate-50 text-slate-500 px-2 py-1 rounded-md border border-slate-100 font-bold uppercase tracking-widest flex items-center gap-1.5">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ formatSchedule(section.schedule) }}
            </span>
          </div>
          <div v-else class="mt-auto pt-2">
            <span class="text-[9px] bg-slate-50 text-slate-400 px-2.5 py-1.5 rounded-md border border-slate-100 font-black uppercase tracking-widest">No schedule set</span>
          </div>
        </div>

        <div class="bg-slate-50/50 border-t border-slate-100 px-5 sm:px-6 py-4 flex items-center justify-between group-hover:bg-pink-50/30 transition-colors">
          <div class="flex items-center gap-5">
            <div class="flex flex-col">
              <span class="text-[8px] font-black uppercase tracking-[0.15em] text-slate-400 mb-0.5">Semester</span>
              <span class="text-xs font-bold text-slate-700">{{ section.semester || 'N/A' }}</span>
            </div>
            <div class="h-7 w-px bg-slate-200"></div>
            <div class="flex flex-col">
              <span class="text-[8px] font-black uppercase tracking-[0.15em] text-slate-400 mb-0.5">Activities</span>
              <span class="text-xs font-bold text-slate-700">{{ section.activity_count || 0 }}</span>
            </div>
          </div>
          <div class="flex items-center justify-center text-slate-300 group-hover:text-pink-500 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="searchQuery && filteredSections.length === 0" class="bg-white rounded-2xl border-2 border-dashed border-slate-200 p-12 text-center">
      <div class="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      </div>
      <h3 class="text-lg font-bold text-slate-700 mb-1">No sections found</h3>
      <p class="text-slate-500 text-sm max-w-xs mx-auto mb-6">
        We couldn't find any sections matching "{{ searchQuery }}".
      </p>
      <button 
        @click="searchQuery = ''"
        class="text-pink-500 font-bold text-sm hover:underline"
      >
        Clear search results
      </button>
    </div>

    <!-- Widgets Area -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-12 mb-8">
      <!-- Recent Activity Widget -->
      <div class="lg:col-span-2 flex flex-col bg-white rounded-2xl shadow-sm border border-slate-100 p-6 min-h-[400px]">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-4 border-b border-slate-100 pb-4 gap-3">
          <h3 class="text-sm font-black text-slate-800 uppercase tracking-widest">Recent Activity</h3>
          <div class="flex items-center gap-1 bg-slate-50 p-1.5 rounded-xl border border-slate-100 overflow-x-auto hide-scrollbar">
            <button @click="setActivityFilter('All')" :class="['px-4 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all whitespace-nowrap', activityFilter === 'All' ? 'bg-white text-slate-800 shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100']">All</button>
            <button @click="setActivityFilter('Submissions')" :class="['px-4 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all whitespace-nowrap', activityFilter === 'Submissions' ? 'bg-white text-slate-800 shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100']">Submissions</button>
            <button @click="setActivityFilter('Activities')" :class="['px-4 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all whitespace-nowrap', activityFilter === 'Activities' ? 'bg-white text-slate-800 shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100']">Activities</button>
            <button @click="setActivityFilter('Students')" :class="['px-4 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all whitespace-nowrap', activityFilter === 'Students' ? 'bg-white text-slate-800 shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100']">Students</button>
          </div>
        </div>

        <div class="flex-1 space-y-4">
          <div v-if="filteredLogs.length === 0" class="py-6 text-slate-400 text-sm italic">
            No recent activity found.
          </div>
          
          <div v-for="log in filteredLogs" :key="log.id" class="flex gap-4 items-start group pb-4 border-b border-slate-50 last:border-0">
            <div class="w-8 h-8 rounded-full bg-slate-50 border border-slate-100 flex items-center justify-center flex-shrink-0 mt-0.5">
              <svg v-html="getLogIcon(log)" class="w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"></svg>
            </div>
            <div class="flex-1">
              <p class="text-[13px] font-medium text-slate-700 leading-snug">{{ log.details || (log.action_type + ' action recorded') }}</p>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400">{{ log.section_name || 'System' }} {{ log.activity_name ? '- ' + log.activity_name : '' }}</span>
                <span class="text-[10px] text-slate-300">&bull;</span>
                <span class="text-[10px] text-slate-400">{{ formatTimeAgo(log.timestamp) }}</span>
              </div>
            </div>
            <div class="text-[9px] uppercase font-bold text-slate-300 tracking-widest mt-1">
              {{ getLogShortAction(log) }}
            </div>
          </div>
        </div>
        
        <div v-if="filteredLogsBase.length > 5" class="flex items-center justify-between mt-6 pt-3 border-t border-slate-200">
          <button 
            @click="logsCurrentPage--" 
            :disabled="logsCurrentPage === 1"
            class="text-[10px] font-bold uppercase tracking-widest text-slate-400 hover:text-slate-800 disabled:opacity-30 disabled:hover:text-slate-400 transition-colors flex items-center gap-1.5"
          >
            &larr; Prev
          </button>
          
          <div class="flex gap-2">
            <button 
              v-for="page in totalLogPages" 
              :key="page"
              @click="logsCurrentPage = page"
              :class="['w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold transition-all', logsCurrentPage === page ? 'bg-slate-800 text-white' : 'text-slate-500 hover:bg-slate-200']"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            @click="logsCurrentPage++" 
            :disabled="logsCurrentPage === totalLogPages"
            class="text-[10px] font-bold uppercase tracking-widest text-slate-400 hover:text-slate-800 disabled:opacity-30 disabled:hover:text-slate-400 transition-colors flex items-center gap-1.5"
          >
            Next &rarr;
          </button>
        </div>
      </div>

      <!-- Class Schedule Widget -->
      <div class="flex flex-col bg-white rounded-2xl shadow-sm border border-slate-100 p-6 min-h-[400px]">
        <div class="flex justify-between items-end mb-6 border-b border-slate-100 pb-4">
          <h3 class="text-sm font-black text-slate-800 uppercase tracking-widest">Schedule</h3>
          <span class="text-[9px] font-black uppercase tracking-widest text-slate-400">Weekly</span>
        </div>

        <div class="flex justify-between mb-6">
          <button 
            v-for="day in daysOfWeek" 
            :key="day"
            @click="selectedScheduleDay = day"
            :class="['text-[10px] font-black uppercase tracking-widest pb-2 border-b-2 transition-all relative', selectedScheduleDay === day ? 'border-slate-800 text-slate-800' : 'border-transparent text-slate-400 hover:text-slate-600 border-b-2']"
          >
            {{ day.substring(0,2) }}
          </button>
        </div>

        <div class="space-y-3">
          <div v-if="scheduleForSelectedDay.length === 0" class="py-4 text-slate-400 text-sm italic">
            No classes scheduled.
          </div>
          
          <div v-for="(sched, index) in scheduleForSelectedDay" :key="index" class="p-4 rounded-xl border border-slate-100 bg-slate-50 hover:bg-slate-100 transition-colors group relative overflow-hidden">
            <div v-if="sched.isToday" class="absolute top-0 right-0 px-2 py-1 bg-pink-100 text-pink-600 text-[8px] font-black uppercase tracking-widest rounded-bl-lg">Today</div>
            
            <h4 class="font-bold text-slate-800 text-xs mb-0.5">{{ sched.section_code }}</h4>
            <p class="text-[11px] text-slate-500 font-medium mb-3">{{ sched.section_name }}</p>
            
            <div class="flex items-center gap-1.5 text-slate-600 font-bold text-[10px] bg-white rounded-md px-2 py-1 border border-slate-100 w-fit">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ sched.start_time }} - {{ sched.end_time }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Section Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] px-4">
      <div class="bg-white rounded-lg shadow-2xl w-full max-w-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="bg-gradient-to-r from-pink-600 to-pink-500 text-white px-6 py-3 flex justify-between items-center rounded-t-lg">
          <h3 class="text-xs font-bold uppercase tracking-widest">Register New Academic Section</h3>
          <button @click="showModal = false" class="text-white hover:text-pink-100 text-2xl transition-colors">&times;</button>
        </div>

        <form @submit.prevent="submitSection" class="p-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <div>
              <label class="block text-xs font-black text-gray-400 uppercase tracking-widest mb-1.5">Section Designation <span class="text-red-500 font-bold">*</span></label>
              <input v-model="form.section_name" type="text" placeholder="e.g., BSIT 3A" class="w-full border border-gray-200 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm font-medium" required>
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Section Code <span class="text-red-500 font-bold">*</span></label>
              <input v-model="form.section_code" type="text" placeholder="e.g., IT311" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Semester <span class="text-red-500 font-bold">*</span></label>
              <select v-model="form.semester" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
                <option value="" disabled>Select Semester</option>
                <option value="1st Semester">1st Semester</option>
                <option value="2nd Semester">2nd Semester</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Academic Year <span class="text-red-500 font-bold">*</span></label>
              <select v-model="form.academic_year" class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50" required>
                <option value="" disabled>Select Year</option>
                <option value="2024-2025">2024-2025</option>
                <option value="2025-2026">2025-2026</option>
                <option value="2026-2027">2026-2027</option>
                <option value="2027-2028">2027-2028</option>
                <option value="2029-2030">2029-2030</option>
              </select>
            </div>
          </div>

          <div class="mb-4">
            <label class="block text-[10px] font-black text-gray-400 uppercase mb-2">Schedule(s)</label>
            <div v-for="(sched, index) in form.schedules" :key="index" class="flex gap-2 mb-2 items-center">
              <select v-model="sched.day" class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm" required>
                <option value="" disabled>Day</option>
                <option value="Monday">Monday</option>
                <option value="Tuesday">Tuesday</option>
                <option value="Wednesday">Wednesday</option>
                <option value="Thursday">Thursday</option>
                <option value="Friday">Friday</option>
                <option value="Saturday">Saturday</option>
                <option value="Sunday">Sunday</option>
              </select>
              <input v-model="sched.start_time" type="time" class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm" required>
              <span class="text-gray-400 text-xs">-</span>
              <input v-model="sched.end_time" type="time" class="flex-1 border rounded-lg px-3 py-2 focus:ring-2 focus:ring-pink-400 outline-none bg-gray-50 text-sm" required>
              <button v-if="form.schedules.length > 1" type="button" @click="removeSchedule(index)" class="text-red-400 hover:text-red-500 p-1">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
            <button type="button" @click="addSchedule" class="text-pink-500 text-[10px] font-bold uppercase tracking-widest hover:text-pink-600 flex items-center gap-1 mt-1 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4" />
              </svg>
              Add Another Schedule
            </button>
          </div>

          <div class="mb-6">
            <label class="block text-[10px] font-black text-gray-400 uppercase mb-1">Description</label>
            <textarea v-model="form.description" rows="3" placeholder="Enter course details..." class="w-full border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-pink-400 outline-none resize-none bg-gray-50"></textarea>
          </div>

          <div class="flex justify-end gap-4 border-t pt-6">
            <button type="button" @click="showModal = false" class="text-gray-400 font-bold uppercase text-xs hover:text-gray-600 transition-colors">Cancel</button>
            <button type="submit" class="px-8 py-3 bg-pink-500 text-white rounded-lg font-black uppercase text-xs shadow-lg active:scale-95 transition-all">Create Section</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { instructorDashboardService } from '@/services/instructor/instructorDashboardService'
import { useNotificationStore } from '@/stores/notification'

const props = defineProps({
  sections: Array
})

const emit = defineEmits(['refresh-data'])

const router = useRouter()
const notificationStore = useNotificationStore()

const searchQuery = ref('')
const showModal = ref(false)
const lastSyncTime = ref(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))

// Form state for creating a new section
const form = ref({
  section_name: '',
  section_code: '',
  semester: '',
  academic_year: '',
  schedules: [{ day: '', start_time: '', end_time: '' }],
  description: ''
})

// State for widgets
const activityLogs = ref([])
const activityFilter = ref('All')
const logsCurrentPage = ref(1)
const logsPageSize = 5
const selectedScheduleDay = ref('Mon')
const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const dayFullNames = { 'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday', 'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday' }

onMounted(async () => {
  // Set current day
  const currentDayIndex = new Date().getDay() // 0=Sun, 1=Mon...
  if (currentDayIndex === 0) {
    selectedScheduleDay.value = 'Sun'
  } else {
    selectedScheduleDay.value = daysOfWeek[currentDayIndex - 1]
  }

  // Fetch recent activity logs
  try {
    const logsData = await instructorDashboardService.getLogs()
    const logsArray = Array.isArray(logsData) ? logsData : (logsData.logs || [])
    activityLogs.value = logsArray.sort((a,b) => b.id - a.id).slice(0, 50)
  } catch(e) {
    console.error('Failed to load logs', e)
  }
})

const addSchedule = () => {
  form.value.schedules.push({ day: '', start_time: '', end_time: '' })
}

const removeSchedule = (index) => {
  form.value.schedules.splice(index, 1)
}

const formatTimeOnly = (t) => {
  if (!t) return ''
  const [h, m] = t.split(':')
  const hour = parseInt(h)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const h12 = hour % 12 || 12
  return `${h12}:${m} ${ampm}`
}

const parsedSectionSchedule = (scheduleData) => {
  if (!scheduleData) return null
  try {
    const schedules = typeof scheduleData === 'string' ? JSON.parse(scheduleData) : scheduleData
    if (Array.isArray(schedules) && schedules.length > 0) return schedules
  } catch (e) {}
  return null
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

const filteredSections = computed(() => {
  if (!searchQuery.value) return props.sections || []
  const query = searchQuery.value.toLowerCase()
  return (props.sections || []).filter(s => 
    s.section_name.toLowerCase().includes(query) || 
    s.section_code.toLowerCase().includes(query)
  )
})

const totalStudents = computed(() => {
  return (props.sections || []).reduce((acc, s) => acc + (s.student_count || 0), 0)
})

const totalActivities = computed(() => {
  return (props.sections || []).reduce((acc, s) => acc + (s.activity_count || 0), 0)
})

const goToSection = (id) => {
  router.push(`/instructor/section/${id}`)
}

const editSection = (section) => {
  router.push(`/instructor/section/${section.id}/settings`)
}

const submitSection = async () => {
  try {
    const payload = {
      ...form.value,
      schedule: JSON.stringify(form.value.schedules)
    }
    await instructorDashboardService.createSection(payload);
    showModal.value = false;
    form.value = { 
      section_name: '', section_code: '', semester: '', 
      academic_year: '', schedules: [{ day: '', start_time: '', end_time: '' }], description: '' 
    };
    emit('refresh-data');
    notificationStore.success("Section created successfully!");
    lastSyncTime.value = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (error) {
    const serverMessage = error.response?.data?.error || "Check if Section Code is unique.";
    notificationStore.error("Backend Error: " + serverMessage);
  }
};

// Activity log filters and formatting
const setActivityFilter = (type) => {
  activityFilter.value = type
  logsCurrentPage.value = 1 // reset limit when switching tabs
}

const filteredLogsBase = computed(() => {
  let logs = activityLogs.value
  if (activityFilter.value !== 'All') {
    logs = logs.filter(log => {
      const type = (log.action_type || '').toUpperCase()
      if (activityFilter.value === 'Students') return type.includes('STUDENT') || type.includes('ENROLL')
      if (activityFilter.value === 'Activities') return type.includes('ACTIVITY') || type.includes('CREATE') || type.includes('UPDATE')
      if (activityFilter.value === 'Submissions') return type.includes('SUBMISSION') || type.includes('GRADE')
      return true
    })
  }
  return logs
})

const totalLogPages = computed(() => {
  return Math.max(1, Math.ceil(filteredLogsBase.value.length / logsPageSize))
})

const filteredLogs = computed(() => {
  const start = (logsCurrentPage.value - 1) * logsPageSize
  return filteredLogsBase.value.slice(start, start + logsPageSize)
})

const getLogIcon = (log) => {
  const t = (log.action_type || '').toUpperCase()
  if (t.includes('SUBMIT') || t.includes('GRADE')) return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />` // green check
  if (t.includes('ENROLL') || t.includes('STUDENT')) return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />` // user add
  return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />` // edit/create pencil
}

const getLogIconStyle = (log) => {
  const t = (log.action_type || '').toUpperCase()
  if (t.includes('SUBMIT') || t.includes('GRADE')) return 'bg-emerald-50 text-emerald-500'
  if (t.includes('ENROLL') || t.includes('STUDENT')) return 'bg-purple-50 text-purple-500'
  return 'bg-amber-50 text-amber-500'
}

const getLogBadgeStyle = (log) => {
  const t = (log.action_type || '').toUpperCase()
  if (t.includes('SUBMIT') || t.includes('GRADE')) return 'bg-emerald-100 text-emerald-600'
  if (t.includes('ENROLL') || t.includes('STUDENT')) return 'bg-purple-100 text-purple-600'
  return 'bg-amber-100 text-amber-600'
}

const getLogShortAction = (log) => {
  const t = (log.action_type || '').toUpperCase()
  if (t.includes('SUBMIT')) return 'Submitted'
  if (t.includes('GRADE')) return 'Graded'
  if (t.includes('ENROLL')) return 'Enrolled'
  if (t.includes('DELETE')) return 'Deleted'
  if (t.includes('ACTIV')) return 'Posted'
  return 'Updated'
}

const formatTimeAgo = (dateStr) => {
  if (!dateStr) return 'Just now'
  const diff = Date.now() - new Date(dateStr).getTime()
  const val = Math.floor(diff / 60000)
  if (val < 1) return 'Just now'
  if (val < 60) return `${val} min ago`
  const hrs = Math.floor(val / 60)
  if (hrs < 24) return `${hrs} hr ago`
  return `${Math.floor(hrs / 24)} days ago`
}

// Map schedule items
const scheduleForSelectedDay = computed(() => {
  const targetDay = dayFullNames[selectedScheduleDay.value]
  let scheds = []
  
  const currentDayIndex = new Date().getDay()
  const todayFullName = currentDayIndex === 0 ? dayFullNames['Sun'] : dayFullNames[daysOfWeek[currentDayIndex - 1]] || ''
  const isToday = targetDay === todayFullName

  ;(props.sections || []).forEach(sec => {
    if (!sec.schedule) return
    try {
      const parsed = typeof sec.schedule === 'string' ? JSON.parse(sec.schedule) : sec.schedule
      if (Array.isArray(parsed)) {
        parsed.forEach(s => {
          if (s.day === targetDay) {
            scheds.push({
              section_name: sec.section_name,
              section_code: sec.section_code,
              start_time: formatTimeOnly(s.start_time),
              end_time: formatTimeOnly(s.end_time),
              original_start: s.start_time,
              isToday: isToday
            })
          }
        })
      }
    } catch(e) {}
  })
  return scheds.sort((a,b) => a.original_start.localeCompare(b.original_start))
})
</script>
