import fs from 'node:fs/promises';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';

const phase = process.argv[2];
const root = 'C:/git-projetos/reliabridge/';
for (const name of ['batch_pre_sizing_casos_materia.xlsx', 'robustez_casos_materia.xlsx', 'engstruct_casos.xlsx']) {
  const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(root + name));
  const range = name === 'engstruct_casos.xlsx' ? 'AD1:AM4' : 'Z1:AI4';
  const preview = await wb.render({ sheetName: 'Casos', range, scale: 1.5, format: 'png' });
  await fs.writeFile(`${root}tmp/limites_casos/${phase}-${name}.png`, new Uint8Array(await preview.arrayBuffer()));
  console.log(name, (await wb.inspect({ kind: 'table', range: `Casos!${range}`, include: 'values,formulas', tableMaxRows: 4, tableMaxCols: 10 })).ndjson);
}
