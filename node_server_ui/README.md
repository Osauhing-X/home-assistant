[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-2.svg
[![Buy me a coffee][buymeacoffee-shield]](https://www.buymeacoffee.com/extaas)


Under Development


## Node stop: SIGTERM, SIGKILL

### Example
process.on('SIGTERM', () => {
  console.log('SIGTERM received – shutting down gracefully');
  // tee puhastus, salvesta andmed, sulge ühendused jne
  process.exit(0); // lõpeta protsess
});