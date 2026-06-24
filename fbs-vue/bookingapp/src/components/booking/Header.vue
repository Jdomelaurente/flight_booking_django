<template>
        <!-- Header -->
    <header class="navbar bg-white relative z-10 py-4 border-b-10 border-[#FF579A] shadow-md">
      <div class="container mx-auto px-5 md:px-10">
        <div class="flex justify-between items-center">
          <!-- Logo -->
          <div class="logo flex items-center gap-3">
            <span class="brand-name font-bold text-[#FF579A] tracking-wide text-2xl">
              LOGO
            </span>
          </div>
          
          <!-- Navigation -->
          <nav class="flex gap-6">
            <router-link 
              to="/" 
              class="text-gray-700 font-medium hover:text-red-600 transition-colors"
              :class="{ 'text-red-600 border-b-2 border-red-600': $route.path === '/' }"
            >
              Book
            </router-link>
            <router-link 
              to="/check-in" 
              class="text-gray-700 font-medium hover:text-red-600 transition-colors"
              :class="{ 'text-red-600 border-b-2 border-red-600': $route.path === '/check-in' }"
            >
              Check-In
            </router-link>
            <router-link 
              to="/status" 
              class="text-gray-700 font-medium hover:text-red-600 transition-colors"
              :class="{ 'text-red-600 border-b-2 border-red-600': $route.path === '/status' }"
            >
              Flight Status
            </router-link>
          </nav>
        </div>
      </div>
    </header>
</template>