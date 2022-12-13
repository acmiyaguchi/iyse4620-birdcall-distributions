<script>
  export let models = [];
  export let regions = [];
  export let species = [];
  export let model;
  export let region;
  export let specie;
  export let should_show = true;
</script>

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
  <!-- checkbox option for should show -->
  <div class="bordered">
    <label>
      <b>trace: </b>
      <input type="checkbox" bind:checked={should_show} />
      show only significant parameters
    </label>
  </div>
</div>

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
