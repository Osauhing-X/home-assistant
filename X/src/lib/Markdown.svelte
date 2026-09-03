<script>
  export let content = '';

  const escapeHtml = (value) => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');

  function inline(value) {
    return escapeHtml(value)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\*([^*]+)\*/g, '<em>$1</em>')
      .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
  }

  function markdown(value) {
    const lines = String(value || '').replaceAll('\r\n', '\n').split('\n');
    const output = [];
    let paragraph = [], list = '', code = [], language = '';

    const closeParagraph = () => {
      if (paragraph.length) output.push(`<p>${inline(paragraph.join(' '))}</p>`);
      paragraph = [];
    };
    const closeList = () => {
      if (list) output.push(`</${list}>`);
      list = '';
    };

    for (const line of lines) {
      const fence = line.match(/^```\s*([\w-]*)/);
      if (fence) {
        closeParagraph(); closeList();
        if (code.length || language) {
          output.push(`<pre><code${language ? ` class="language-${escapeHtml(language)}"` : ''}>${escapeHtml(code.join('\n'))}</code></pre>`);
          code = []; language = '';
        } else language = fence[1] || 'text';
        continue;
      }
      if (language) { code.push(line); continue; }
      const heading = line.match(/^(#{1,6})\s+(.+)$/);
      const unordered = line.match(/^\s*[-*+]\s+(.+)$/);
      const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
      if (heading) {
        closeParagraph(); closeList();
        const level = heading[1].length;
        output.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      } else if (unordered || ordered) {
        closeParagraph();
        const kind = ordered ? 'ol' : 'ul';
        if (list !== kind) { closeList(); output.push(`<${kind}>`); list = kind; }
        output.push(`<li>${inline((ordered || unordered)[1])}</li>`);
      } else if (/^\s*---+\s*$/.test(line)) {
        closeParagraph(); closeList(); output.push('<hr>');
      } else if (!line.trim()) {
        closeParagraph(); closeList();
      } else paragraph.push(line.trim());
    }
    closeParagraph(); closeList();
    if (language) output.push(`<pre><code class="language-${escapeHtml(language)}">${escapeHtml(code.join('\n'))}</code></pre>`);
    return output.join('\n');
  }

  $: html = markdown(content);
</script>

<article class="markdown">{@html html}</article>

<style>
  .markdown{max-width:1000px;color:#b8c1cc;line-height:1.72;overflow-wrap:anywhere}
  .markdown :global(h1),.markdown :global(h2),.markdown :global(h3),.markdown :global(h4){color:#f1f3f6;line-height:1.25;letter-spacing:-.02em}
  .markdown :global(h1){margin:0 0 22px;font-size:30px}.markdown :global(h2){margin:34px 0 12px;font-size:21px}.markdown :global(h3){margin:26px 0 10px;font-size:16px}.markdown :global(h4){margin:22px 0 8px;font-size:14px}
  .markdown :global(p){margin:0 0 16px}.markdown :global(ul),.markdown :global(ol){margin:0 0 18px;padding-left:25px}.markdown :global(li){margin:5px 0}.markdown :global(li)::marker{color:#da3}
  .markdown :global(strong){color:#eef1f4}.markdown :global(a){color:#e1b93b;text-decoration:underline;text-underline-offset:3px}.markdown :global(hr){margin:30px 0;border:0;border-top:1px solid #29313b}
  .markdown :global(code){padding:2px 5px;border:1px solid #303844;border-radius:4px;background:#111820;color:#efc84a;font:12px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace}
  .markdown :global(pre){margin:18px 0;padding:16px;overflow:auto;border:1px solid #29313b;border-radius:8px;background:#06090d}.markdown :global(pre code){padding:0;border:0;background:transparent;color:#d8dee7}
</style>
