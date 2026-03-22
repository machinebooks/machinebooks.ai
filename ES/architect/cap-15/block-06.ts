// Extraído de: LibroTecnico/cap-15-interfaces-chat.md
interface MentionContext {
  type: 'proposal' | 'client' | 'opportunity' | 'document';
  id: string;
  displayText: string;
}

export function parseMentions(text: string): {
  cleanText: string;
  mentions: MentionContext[];
} {
  const mentionRegex = /@(propuesta|cliente|oportunidad|doc):([^c15-\s]+)/g;
  const mentions: MentionContext[] = [];

  const cleanText = text.replace(mentionRegex, (match, type, id) => {
    const typeMap: Record<string, MentionContext['type']> = {
      'propuesta': 'proposal',
      'cliente': 'client',
      'oportunidad': 'opportunity',
      'doc': 'document'
    };

    mentions.push({
      type: typeMap[type],
      id: id,
      displayText: match
    });

    return `[${type}:${id}]`;  // Placeholder en el texto limpio
  });

  return { cleanText, mentions };
}
