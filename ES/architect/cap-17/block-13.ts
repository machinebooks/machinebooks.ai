// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
      toggleSelection: (id) =>
        set((state) => {
          const newSelected = new Set(state.selectedIds);
          if (newSelected.has(id)) {
            newSelected.delete(id);
          } else {
            newSelected.add(id);
          }
          return { selectedIds: newSelected };
        }),

      clearSelection: () => set({ selectedIds: new Set() }),
    }),
    { name: 'OperationsUI' }  // Nombre en Redux DevTools
  )
);
