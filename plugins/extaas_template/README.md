https://my.home-assistant.io/redirect/config_flow_start/?domain=extaas_template

http://home.local:8123/config/integrations/integration/extaas_template







































kuidas ma node rakendusega muid andmeid edastan.


nt str andmed ja boolena andmeid ja int andmeid,

objektina: {
   status: "SENDING",
   web: true,
   request: 323,
   update_avaible: true,
}


et umbes sellien suvaline objekt millest genereeritakse entity-s

kuna iga node rakendus edastab erinevaid andmeid siis see entity loomine peab olema dynaamiline. Kui seade/node HA-st kustutatakse kustuvad ka need node poolt tekkinud entity-d.

KUID on pisike asi kui node enam ei edasta mingit objecti sisu siis see mida ta ei esita enam kustuta.


Et nt algul saatsin jah: {
   status: "SENDING",
   web: true,
   request: 323,
   update_avaible: true,
}

aga vahepeal uuentati node ja objekti sisu muutus: {
  status: "SENDING",
  website: true,
  request: 323,
  id: "sf_32423"
}

siis web ja update_avaible kustutatakse listist. See juhtub ainult siis kui nodejs tulnud objekt ei ole enam sama mis ennem ehk POST oleks trigger ise HA ei tohiks seda otsutada, ennem kui pole andmed tulnud. 