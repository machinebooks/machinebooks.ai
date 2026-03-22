# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
# Crear espacio de trabajo
WORKDIR /lab
RUN mkdir -p /lab/{drivers,scripts,results,ghidra-scripts,symbols}

# Copiar scripts y drivers de anÃ¡lisis
COPY scripts/ /lab/scripts/
COPY drivers/ /lab/drivers/

# ConfiguraciÃ³n inicial de radare2
RUN echo 'e scr.color=3' > /root/.radare2rc && \
    echo 'e asm.syntax=intel' >> /root/.radare2rc && \
    echo 'e anal.jmp.mid=true' >> /root/.radare2rc

ENTRYPOINT ["/bin/bash"]
