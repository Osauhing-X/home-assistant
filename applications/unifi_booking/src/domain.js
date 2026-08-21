import { randomUUID } from 'node:crypto';

export const ROOM_STATES = ['ready','reserved','occupied','cleaning','inspection','maintenance','needs_attention','exclusive','staff','utility'];

export function transitionRoom(room, event, now = new Date().toISOString()) {
  const allowed = {
    reserve: ['ready'], check_in: ['reserved','ready'], check_out: ['occupied'],
    start_cleaning: ['needs_attention','occupied'], request_attention: ROOM_STATES,
    start_inspection: ['cleaning'], start_maintenance: ['needs_attention','inspection'],
    mark_ready: ['cleaning','inspection','maintenance','needs_attention']
  };
  if (!allowed[event]?.includes(room.state)) throw new Error(`Cannot ${event} from ${room.state}`);
  const state = ({reserve:'reserved',check_in:'occupied',check_out:'needs_attention',start_cleaning:'cleaning',request_attention:'needs_attention',start_inspection:'inspection',start_maintenance:'maintenance',mark_ready:'ready'})[event];
  return {...room,state,updated_at:now};
}

export function createCredential({guest_id, room_ids, type, value, valid_from, valid_until}) {
  if (!['qr','pin','license_plate','card'].includes(type)) throw new Error('Unsupported credential type');
  if (!guest_id || !room_ids?.length || !value || !valid_until) throw new Error('Credential is incomplete');
  if (new Date(valid_until) <= new Date(valid_from || 0)) throw new Error('Credential expiry must be after start');
  return {id:randomUUID(),guest_id,room_ids:[...new Set(room_ids)],type,value,valid_from,valid_until,status:'pending'};
}

export function workflowProgress(tasks) {
  if (!tasks.length) return 100;
  return Math.round(tasks.filter(t => t.status === 'done' || t.status === 'skipped').length / tasks.length * 100);
}
