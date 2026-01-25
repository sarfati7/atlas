import { create } from 'zustand'

interface DraftState {
  content: string
  originalContent: string
  isDirty: boolean

  setContent: (content: string) => void
  setOriginalContent: (content: string) => void
  resetDraft: () => void
  discardChanges: () => void
}

export const useDraftStore = create<DraftState>((set, get) => ({
  content: '',
  originalContent: '',
  isDirty: false,

  setContent: (content) => {
    const { originalContent } = get()
    set({
      content,
      isDirty: content !== originalContent,
    })
  },

  setOriginalContent: (content) => {
    set({
      originalContent: content,
      content,
      isDirty: false,
    })
  },

  resetDraft: () => {
    set({
      content: '',
      originalContent: '',
      isDirty: false,
    })
  },

  discardChanges: () => {
    const { originalContent } = get()
    set({
      content: originalContent,
      isDirty: false,
    })
  },
}))
