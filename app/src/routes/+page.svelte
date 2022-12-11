<script>
  import { onMount } from "svelte";
  import { uniq } from "lodash";
  import Table from "$lib/Table.svelte";

  const url = import.meta.env.VITE_HOST || "http://localhost:4000/data";

  let manifest = [];
  let model = "intercept_car";
  let region = "americas";
  let specie = null;

  let trace = [];

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

<h1>IYSE 4620 Birdcall Distributions</h1>

<p />
Anthony Miyaguchi, 2022-12-11

<p>
  See the source on <a href="https://github.com/acmiyaguchi/iyse4620-birdcall-distributions"
    >GitHub</a
  > for more details.
</p>

<!--this div will end up being the left hand model-->
<div class="menu">
  <div class="bordered">
    <!--title is left of the options-->
    <b>models: </b>
    <!-- radio input for models -->
    {#each models as item}
      <label>
        <input type="radio" bind:group={model} value={item} />
        {item}
      </label>
    {/each}
  </div>
  <div class="bordered">
    <b>regions: </b>
    <!-- radio with a choice of region -->
    {#each regions as item}
      <label>
        <input type="radio" bind:group={region} value={item} />
        {item}
      </label>
    {/each}
  </div>
  <div class="bordered">
    <b>species: </b>
    <!-- dropdown with a choice of specie -->
    {#each species as item}
      <label>
        <input type="radio" bind:group={specie} value={item} />
        {item}
      </label>
    {/each}
  </div>
</div>

<!-- now we show the actual images; we can break this out into another component
if we really wanted to. -->
{#if selected}
  <h2>{specie}, {region}, {selected.grid_size} degree solution</h2>
  <h3>plots</h3>
  <div class="primary">
    <div>
      <h4>linear scale</h4>
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
  <h3>trace summary</h3>
  {#if trace.length > 0}
    <div>
      <h4>misc parameters</h4>
      <!-- for some reason, we can't filter out betas directly (???)-->
      <Table data={trace.filter((x) => !x.index.includes("phi[") && !x.index.includes("mu["))} />
    </div>

    <div>
      <h4>spatial random effect phi</h4>
      <Table data={trace.filter((x) => x.index.includes("phi["))} paginationSize={10} />
    </div>
    <div>
      <h4>poisson prior mu</h4>

      <Table data={trace.filter((x) => x.index.includes("mu["))} paginationSize={10} />
    </div>
  {/if}
{/if}

<style>
  /* add padding between menu items */
  .menu > div {
    padding: 5px;
    max-width: 600px;
  }
  .bordered {
    /* make these so they have a thin border */
    border: 1px solid black;
  }
</style>
