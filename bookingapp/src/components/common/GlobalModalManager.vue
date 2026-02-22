<template>
  <BaseModal 
    :is-open="modalStore.isOpen" 
    @close="modalStore.close(false)"
    :compact="modalStore.type !== 'custom'"
  >
    <PremiumDeleteModal 
      v-if="modalStore.variant === 'danger'"
      :title="modalStore.title"
      :message="modalStore.message"
      :confirm-text="modalStore.confirmText"
      :cancel-text="modalStore.cancelText"
      :loading="modalStore.isLoading"
      :loading-text="modalStore.loadingText"
      variant="danger"
      @confirm="modalStore.close(true)"
      @cancel="modalStore.close(false)"
    />
    <ConfirmationModal v-else-if="modalStore.type === 'confirm' || modalStore.type === 'alert'" />
    
    <!-- Placeholder for other custom modals if needed -->
    <div v-else-if="modalStore.type === 'custom'" class="p-6">
      <slot name="custom"></slot>
    </div>
  </BaseModal>
</template>

<script setup>
import { useModalStore } from '@/stores/modal';
import BaseModal from './BaseModal.vue';
import ConfirmationModal from './ConfirmationModal.vue';
import PremiumDeleteModal from './PremiumDeleteModal.vue';

const modalStore = useModalStore();
</script>
