```
  import { base } from '$app/paths';
  <a href={base + '/sv'}>Movies 2</a>

  base -> "/api/hassio_ingress/0tePT97nBNgQv0oOBr9A_N6w0B6xR4ru2vLXJsQqIO0" + "/sv"
```

```
  import { resolve } from '$app/paths';
  <a href={resolve('/sv')}>Movies 2</a>

  resolve -> "http://home.local:8123/api/hassio_ingress/0tePT97nBNgQv0oOBr9A_N6w0B6xR4ru2vLXJsQqIO0/sv"
```