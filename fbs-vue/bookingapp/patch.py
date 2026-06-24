import sys
import re

file_path = r'c:\Users\user\OneDrive\Desktop\Folders\Fbs\fbs-vue\bookingapp\src\views\Instructor\instructor_dashboard.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = r'<div \n        v-for="section in filteredSections"'
# find exactly where the grid ends.
import re
match = re.search(r'(<div \n        v-for="section in filteredSections".*?</div>\n      </div>)\n    </div>\n\n    <!-- Empty State -->', content, re.DOTALL)

if match:
    old_block = match.group(1)
    new_card = """<div 
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
      </div>"""
    content = content.replace(old_block, new_card)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success")
else:
    print("Match failed")
