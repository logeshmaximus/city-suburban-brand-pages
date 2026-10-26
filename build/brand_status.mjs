// Brand page status from Sanity (service-page project boolyxr0) + whether the live page loads.
//   node --env-file=<service-page .env.local> brand_status.mjs <drafts.json> <out status.json>
import fs from 'node:fs'
const [, , draftsFile, out] = process.argv
const titles = JSON.parse(fs.readFileSync(draftsFile, 'utf8'))   // sheet title → page slug
const token = process.env.SANITY_API_READ_TOKEN
const q = encodeURIComponent('*[_type=="brandPage"]{_id,"slug":slug.current,"brand":meta.brand}')
const docs = (await (await fetch(`https://boolyxr0.api.sanity.io/v2024-01-01/data/query/production?perspective=raw&query=${q}`, {headers: {Authorization: `Bearer ${token}`}})).json()).result
const slugify = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
const result = {}
for (const [title, slug] of Object.entries(titles)) {
  const mine = docs.filter((d) => d._id.replace(/^drafts\./, '').endsWith(slug) || d.slug === slug)
  const published = mine.find((d) => !d._id.startsWith('drafts.'))
  const brand = published?.brand || mine[0]?.brand || title.split(' ')[0]
  const path = `/services/${slugify(brand)}/${slug}/`
  let live = false
  if (published) live = (await fetch(`https://citysuburbanheating.com${path}`, {redirect: 'follow'})).status === 200
  result[title] = {slug, path, status: published ? 'published' : mine.length ? 'draft' : 'none', live}
  console.log(result[title].status.padEnd(10), live ? 'LIVE' : '    ', title)
}
fs.writeFileSync(out, JSON.stringify(result, null, 1))
