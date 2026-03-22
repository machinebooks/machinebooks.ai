// Extraído de: LibroTecnico/cap-15-interfaces-chat.md
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';

interface Notification {
  id: number;
  type: 'NEW_OPPORTUNITY' | 'DEAL_STALLED' | 'ACCOUNT_RISK' |
        'REPORT_READY' | 'OPPORTUNITY_MATCH' | 'SYSTEM';
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  body: string;
  action_url?: string;
  extra_data?: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

// Icono y color por tipo de notificación para renderizado visual diferenciado
const NOTIFICATION_META: Record<string, { icon: string; color: string }> = {
  NEW_OPPORTUNITY:    { icon: '🎯', color: 'blue' },
  DEAL_STALLED:       { icon: '⏸️', color: 'amber' },
  ACCOUNT_RISK:       { icon: '⚠️', color: 'red' },
  REPORT_READY:       { icon: '📊', color: 'green' },
  OPPORTUNITY_MATCH:  { icon: '✨', color: 'purple' },
  SYSTEM:             { icon: 'ℹ️', color: 'gray' }
};

export function useNotifications() {
  const queryClient = useQueryClient();

  // Polling cada 30 segundos para notificaciones no leídas
  const { data: notifications = [] } = useQuery<Notification[]>({
    queryKey: ['notifications', 'unread'],
    queryFn: () => api.get('/notifications?is_read=false').then(r => r.data),
    refetchInterval: 30_000,
    staleTime: 25_000
  });

  const markAsRead = useMutation({
    mutationFn: (notificationId: number) =>
      api.patch(`/notifications/${notificationId}/read`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    }
  });

  const unreadCount = notifications.filter(n => !n.is_read).length;
  const highPriorityCount = notifications.filter(
    n => !n.is_read && n.priority === 'HIGH'
  ).length;

  return {
    notifications,
    unreadCount,
    highPriorityCount,
    markAsRead: markAsRead.mutate,
    meta: NOTIFICATION_META
  };
}
