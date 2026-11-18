/**
 * Oculomics — organize BRSET diagnosis shortcuts (private Google Apps Script).
 *
 * Use in script.google.com signed into your individually authorized account.
 * In Project Settings > Script properties, configure:
 *   BRSET_CSV_ID        ID of private label_brset.csv file
 *   BRSET_IMAGES_ID     ID of original fundus_photos folder
 *   BRSET_DIAGNOSES_ID  ID of "diagnosticos_multirrotulo_REFERENCIA" parent
 *
 * Run organizeNextBatch repeatedly until it logs "FINISHED".
 * Each execution processes 100 source image files; does not delete/move originals.
 * It creates Google Drive shortcuts (not copies) for all positive labels.
 *
 * WARNING: Shortcuts may expose access requests or metadata to folder viewers.
 * Do not share diagnosis folders broadly or publicly.
 */
const DIAGNOSES = {
  diabetic_retinopathy: 'retinopatia_diabetica',
  macular_edema: 'edema_macular',
  hypertensive_retinopathy: 'retinopatia_hipertensiva',
  hemorrhage: 'hemorragia',
  vascular_occlusion: 'oclusao_vascular',
  amd: 'degeneracao_macular',
  drusen: 'drusas',
  retinal_detachment: 'descolamento_retina',
  increased_cup_disc: 'escavacao_papilar_aumentada',
  myopic_fundus: 'fundo_miopico',
  scar: 'cicatriz',
  nevus: 'nevo',
  other: 'outras_alteracoes'
};
function config_(key) {
  const value=PropertiesService.getScriptProperties().getProperty(key);
  if (!value) throw new Error('Missing script property: '+key);
  return value;
}
function folder_(parent, name) {
  const matches=parent.getFoldersByName(name);
  return matches.hasNext()?matches.next():parent.createFolder(name);
}
function readLabels_() {
  const blob=DriveApp.getFileById(config_('BRSET_CSV_ID')).getBlob();
  const rows=Utilities.parseCsv(blob.getDataAsString('UTF-8'));
  const cols=rows.shift();
  const idx={};cols.forEach((col,i)=>idx[col]=i);
  for(const name of ['image_id',...Object.keys(DIAGNOSES)]){
    if(idx[name]===undefined)throw new Error('Missing column '+name);
  }
  const mapping=new Map();
  for(const row of rows) {
    const imageId=row[idx.image_id];
    const positives=Object.keys(DIAGNOSES).filter(k=>row[idx[k]]==='1');
    mapping.set(imageId, positives);
  }
  return mapping;
}
function organizeNextBatch() {
  const properties=PropertiesService.getScriptProperties();
  const iteratorToken=properties.getProperty('BRSET_CONTINUATION_TOKEN');
  const folder=DriveApp.getFolderById(config_('BRSET_IMAGES_ID'));
  const dest=DriveApp.getFolderById(config_('BRSET_DIAGNOSES_ID'));
  const map=readLabels_();
  const destinations={};
  for(const [label,name] of Object.entries(DIAGNOSES)) {
    destinations[label]=folder_(dest,name);
  }
  const iterator=iteratorToken ? DriveApp.continueFileIterator(iteratorToken) : folder.getFiles();
  let processed=0, created=0, unknown=0;
  while(iterator.hasNext() && processed<100) {
    const file=iterator.next();
    const match=/^(img\d+)\.jpg$/i.exec(file.getName());
    processed++;
    if (!match)continue;
    const classes=map.get(match[1]);
    if (!classes){unknown++;continue;}
    for(const label of classes){
      const destination=destinations[label];
      // Idempotent per folder/name: repeated execution won't create another shortcut.
      if(destination.getFilesByName(file.getName()).hasNext())continue;
      const shortcut=DriveApp.createShortcut(file.getId());
      shortcut.setName(file.getName());
      shortcut.moveTo(destination);
      created++;
    }
  }
  if(iterator.hasNext()) {
    properties.setProperty('BRSET_CONTINUATION_TOKEN',iterator.getContinuationToken());
    console.log('Batch processed: '+processed+', new shortcuts: '+created+', unmatched images: '+unknown+'. Run again.');
  } else {
    properties.deleteProperty('BRSET_CONTINUATION_TOKEN');
    properties.setProperty('BRSET_FINISHED','true');
    console.log('FINISHED. Last batch: '+processed+', new shortcuts: '+created+'.');
  }
}
function resetCursorOnly() {
  PropertiesService.getScriptProperties().deleteProperty('BRSET_CONTINUATION_TOKEN');
  PropertiesService.getScriptProperties().deleteProperty('BRSET_FINISHED');
  console.log('Cursor reset. Existing shortcuts are preserved; duplicate names are skipped.');
}
