import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(__dirname, '..')

const tokensPath = path.join(rootDir, 'design-tokens.json')
const jsOutputPath = path.join(rootDir, 'src', 'plugins', 'theme.generated.js')
const scssOutputPath = path.join(rootDir, 'src', 'styles', '_tokens.scss')
const coreThemeCssPath = path.resolve(rootDir, '..', '..', 'equipose-core', 'shared-ui', 'equipose-theme.css')

function loadTokens() {
  const rawData = fs.readFileSync(tokensPath, 'utf8')
  return JSON.parse(rawData)
}

function camelToKebab(str) {
  return str.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase()
}

function generateThemeArtifacts() {
  const tokenData = loadTokens()
  const colorTokens = tokenData.tokens?.color?.brand || {}

  // Vuetify theme color map
  const vuetifyColors = {
    primary: colorTokens.primary?.value || '#193074',
    secondary: colorTokens.secondary?.value || '#0066F8',
    accent: colorTokens.accent?.value || '#2196f3',
    error: tokenData.tokens?.color?.brand?.feedback?.error?.value || '#f44336',
    warning: tokenData.tokens?.color?.brand?.feedback?.warning?.value || '#996500',
    info: tokenData.tokens?.color?.brand?.feedback?.info?.value || '#0a56c2',
    success: tokenData.tokens?.color?.brand?.feedback?.success?.value || '#4caf50',
    green: tokenData.tokens?.color?.brand?.feedback?.green?.value || '#3f9c35',
    red: tokenData.tokens?.color?.brand?.feedback?.red?.value || '#e6553f',
    orange: tokenData.tokens?.color?.brand?.feedback?.orange?.value || '#FF9800',
    dfltBackground: tokenData.tokens?.color?.brand?.background?.default?.value || '#f2f7fd',
    dfltBackgroundLight1: tokenData.tokens?.color?.brand?.background?.defaultLight1?.value || '#B1D5F2',
    dfltBackgroundLight2: tokenData.tokens?.color?.brand?.background?.defaultLight2?.value || '#D8EAF8',
    greyBackground: tokenData.tokens?.color?.brand?.background?.grey?.value || '#ebe8e5',
    nnLightBlue1: colorTokens.nnLightBlue1?.value || '#334784',
    nnLightBlue2: colorTokens.nnLightBlue2?.value || '#6675a3',
    nnLightBlue3: colorTokens.nnLightBlue3?.value || '#99a6cc',
    nnLightBlue4: colorTokens.nnLightBlue4?.value || '#e5e8ef',
    nnDarkBlue1: colorTokens.nnDarkBlue1?.value || '#2267c8',
    nnGreen1: colorTokens.nnGreen1?.value || '#2a918b',
    nnPink1: colorTokens.nnPink1?.value || '#eea7bf',
    parameterBackground: tokenData.tokens?.color?.brand?.background?.parameter?.value || '#E0E0E0',
    crfCollection: tokenData.tokens?.color?.brand?.crf?.collection?.value || '#193074',
    crfForm: tokenData.tokens?.color?.brand?.crf?.form?.value || '#005AD2',
    crfGroup: tokenData.tokens?.color?.brand?.crf?.group?.value || '#3B97DE',
    crfItem: tokenData.tokens?.color?.brand?.crf?.item?.value || '#63A8A5',
    darkGrey: tokenData.tokens?.color?.brand?.text?.darkGrey?.value || '#747474',
    tableGray: tokenData.tokens?.color?.brand?.table?.gray?.value || '#E5E5E5',
    vTransparent: tokenData.tokens?.color?.brand?.palette?.vTransparent?.value || '#FFFFFF00',
    nnWhite: tokenData.tokens?.color?.brand?.palette?.nnWhite?.value || '#FFFFFF',
    nnBaseBlue: tokenData.tokens?.color?.brand?.palette?.nnBaseBlue?.value || '#005BD2',
    nnTrueBlue: tokenData.tokens?.color?.brand?.palette?.nnTrueBlue?.value || '#001965',
    nnBaseGray: tokenData.tokens?.color?.brand?.palette?.nnBaseGray?.value || '#939AA7',
    nnBaseHeavy: tokenData.tokens?.color?.brand?.palette?.nnBaseHeavy?.value || '#E8EAF0',
    nnBaseLight: tokenData.tokens?.color?.brand?.palette?.nnBaseLight?.value || '#F7F8FA',
    nnGray200: tokenData.tokens?.color?.brand?.palette?.nnGray200?.value || '#E9EAED',
    nnGray300: tokenData.tokens?.color?.brand?.palette?.nnGray300?.value || '#D3D6DB',
    nnSeaBlue3: tokenData.tokens?.color?.brand?.palette?.nnSeaBlue3?.value || '#91B8EC',
    nnSeaBlue100: tokenData.tokens?.color?.brand?.palette?.nnSeaBlue100?.value || '#E5F1FF',
    nnSeaBlue200: tokenData.tokens?.color?.brand?.palette?.nnSeaBlue200?.value || '#CCE2FF',
    nnSeaBlue300: tokenData.tokens?.color?.brand?.palette?.nnSeaBlue300?.value || '#99C5FF',
    nnSeaBlue400: tokenData.tokens?.color?.brand?.palette?.nnSeaBlue400?.value || '#66A8FF',
    nnSeaBlue700: tokenData.tokens?.color?.brand?.palette?.nnSeaBlue700?.value || '#0049A9',
    nnSeaBlue900: tokenData.tokens?.color?.brand?.palette?.nnSeaBlue900?.value || '#002C66',
    nnLightBlue100: tokenData.tokens?.color?.brand?.palette?.nnLightBlue100?.value || '#F4F5F8',
    nnLightBlue200: tokenData.tokens?.color?.brand?.palette?.nnLightBlue200?.value || '#D7EAF8',
    nnFadedBlue200: tokenData.tokens?.color?.brand?.palette?.nnFadedBlue200?.value || '#DEE1EB',
    nnGoldenSun200: tokenData.tokens?.color?.brand?.palette?.nnGoldenSun200?.value || '#FAEECC',
    nnGraniteGrey1: tokenData.tokens?.color?.brand?.palette?.nnGraniteGrey1?.value || '#f4f5f6',
    tableParentExpanded: tokenData.tokens?.color?.brand?.table?.parentExpanded?.value || '#C2D8F4',
    tableChildRow: tokenData.tokens?.color?.brand?.table?.childRow?.value || '#E6EFFB',
    nnTableRowExpanded: tokenData.tokens?.color?.brand?.table?.rowExpanded?.value || '#C2D8F4',
    nnTableRowChild: tokenData.tokens?.color?.brand?.table?.rowChild?.value || '#E6EFFB',
    nnAlertRed: tokenData.tokens?.color?.brand?.feedback?.alertRed?.value || '#C44836'
  }

  // Generate JS Theme File
  const jsContent = `// Automatically generated by scripts/compile-tokens.js - DO NOT EDIT DIRECTLY
export const themeColors = ${JSON.stringify(vuetifyColors, null, 2)}
export default themeColors
`
  fs.mkdirSync(path.dirname(jsOutputPath), { recursive: true })
  fs.writeFileSync(jsOutputPath, jsContent, 'utf8')
  console.log(`[Token Compiler] Generated ${jsOutputPath}`)

  // Generate SCSS / CSS Custom Properties File
  const cssVars = []
  cssVars.push(`  --primary-color: ${vuetifyColors.primary};`)
  cssVars.push(`  --primary-hover: #102354;`)
  cssVars.push(`  --color-bg-main: ${tokenData.tokens?.color?.brand?.background?.main?.value || '#012169'};`)
  cssVars.push(`  --color-bg-default: ${vuetifyColors.dfltBackground};`)
  cssVars.push(`  --color-bg-white: #ffffff;`)
  cssVars.push(`  --color-text-white: #ffffff;`)
  cssVars.push(`  --color-text-primary: #212529;`)

  for (const [key, val] of Object.entries(vuetifyColors)) {
    const kebab = camelToKebab(key)
    cssVars.push(`  --color-${kebab}: ${val};`)
  }

  const scssContent = `// Automatically generated by scripts/compile-tokens.js - DO NOT EDIT DIRECTLY
:root {
${cssVars.join('\n')}
}
`
  fs.mkdirSync(path.dirname(scssOutputPath), { recursive: true })
  fs.writeFileSync(scssOutputPath, scssContent, 'utf8')
  console.log(`[Token Compiler] Generated ${scssOutputPath}`)

  // Update equipose-core shared theme if path exists
  if (fs.existsSync(coreThemeCssPath)) {
    let coreCss = fs.readFileSync(coreThemeCssPath, 'utf8')
    coreCss = coreCss.replace(/--primary-color:\s*#[0-9a-fA-F]+;/g, `--primary-color: ${vuetifyColors.primary};`)
    fs.writeFileSync(coreThemeCssPath, coreCss, 'utf8')
    console.log(`[Token Compiler] Updated ${coreThemeCssPath}`)
  }
}

generateThemeArtifacts()
