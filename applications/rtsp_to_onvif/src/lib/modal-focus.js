let openDialogs=0,previousOverflow='';
export function modalFocus(node,options){
 const previous=document.activeElement;
 if(typeof node.showModal==='function'&&!node.open)node.showModal();
 if(openDialogs++===0){previousOverflow=document.body.style.overflow;document.body.style.overflow='hidden';}
 const focusable=()=>[...node.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[tabindex]:not([tabindex="-1"])')].filter(item=>!item.disabled&&item.getClientRects().length);
 const initial=node.querySelector('input:not([disabled]),select:not([disabled]),textarea:not([disabled])')||focusable()[0]||node;
 queueMicrotask(()=>{if(node.isConnected)initial.focus();});
 const keydown=event=>{
  if(event.key==='Escape'){event.preventDefault();event.stopPropagation();options?.onClose?.();return;}
  if(event.key!=='Tab')return;
  const items=focusable(),first=items[0],last=items.at(-1);
  if(!first){event.preventDefault();node.focus();return;}
  if(event.shiftKey&&(document.activeElement===first||document.activeElement===node)){event.preventDefault();last.focus();}
  else if(!event.shiftKey&&(document.activeElement===last||document.activeElement===node)){event.preventDefault();first.focus();}
 };
 node.addEventListener('keydown',keydown);
 const cancel=event=>{event.preventDefault();options?.onClose?.();};node.addEventListener('cancel',cancel);
 return {update(value){options=value;},destroy(){node.removeEventListener('keydown',keydown);node.removeEventListener('cancel',cancel);if(node.open)node.close();if(--openDialogs===0)document.body.style.overflow=previousOverflow;if(previous?.isConnected)previous.focus();}};
}
