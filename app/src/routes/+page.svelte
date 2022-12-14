<script>
  import { onMount } from "svelte";
  import { uniq } from "lodash-es";
  import FrontMatter from "$lib/docs/FrontMatter.md";
  import PlotMatter from "$lib/docs/PlotMatter.md";
  import TraceMatter from "$lib/docs/TraceMatter.md";
  import ModelOptions from "./ModelOptions.svelte";
  import TraceSummary from "./TraceSummary.md";
  import DataMatter from "$lib/docs/DataMatter.md";

  const url =
    import.meta.env.VITE_HOST ||
    "https://storage.googleapis.com/iyse6420-birdcall-distribution/processed";

  let manifest = [];
  let model = "intercept_covariate_car";
  let region = "americas";
  let specie = null;

  // for trace data
  let trace = [];
  let should_show = true;

  onMount(async () => {
    const res = await fetch(`${url}/manifest.json`);
    manifest = await res.json();
  });

  $: models = uniq(manifest.map((item) => item.model));
  $: regions = uniq(manifest.map((item) => item.region));

  $: filtered_manifest = manifest.filter((item) => item.model === model && item.region === region);

  $: species = uniq(filtered_manifest.map((item) => item.primary_label));
  // change the currently selected specie if other choices change; we default to the
  // first item in the species list
  $: model && region && species && !species.includes(specie) && (specie = species[0]);

  $: selected = filtered_manifest.find((item) => item.primary_label === specie);

  // trace data
  $: specie &&
    fetch(`${url}/${selected.path}/${selected.traces.trace}`)
      .then((res) => res.json())
      .then((data) => (trace = [...data]));
  // NOTE: we don't really need the ppc data atm, but we could use it to show a
  // histogram or something

  $: console.log(trace.filter((x) => x.index.includes("beta")));
</script>

<h1>IYSE 6420 Birdcall Distributions</h1>

<FrontMatter />

<h2>Plots</h2>

<PlotMatter />

<h3>Options</h3>

<ModelOptions {models} {regions} {species} bind:model bind:region bind:specie />

{#if selected}
  <h3>
    {specie},
    {region},
    {selected.grid_size} degree resolution,
    {trace.filter((x) => x.index.includes("phi[")).length} cells
  </h3>
  <div class="primary">
    <h4>linear scale</h4>
    <div>
      <img
        src={`${url}/${selected.path}/${selected.images.observed_linear}`}
        alt="observed, linear"
      />
      <img src={`${url}/${selected.path}/${selected.images.ppc_linear}`} alt="ppc, linear" />
    </div>
    <h4>log scale</h4>
    <div>
      <img src={`${url}/${selected.path}/${selected.images.observed_log}`} alt="observed, log" />
      <img src={`${url}/${selected.path}/${selected.images.ppc_log}`} alt="ppc, log" />
    </div>
  </div>

  <h2>Trace Summary</h2>

  <TraceMatter />

  <h3>options</h3>

  <ModelOptions {models} {regions} {species} bind:model bind:region bind:specie bind:should_show />

  <h3>
    {specie},
    {region},
    {selected.grid_size} degree resolution,
    {trace.filter((x) => x.index.includes("phi[")).length} cells
  </h3>

  <TraceSummary {trace} {should_show} />
{/if}

<h2>Data</h2>

<DataMatter />

<style>
  img {
    max-width: 450px;
  }
  .primary {
    text-align: center;
  }

  @media (max-width: 450px) {
    img {
      max-width: 100%;
    }
  }
</style>
