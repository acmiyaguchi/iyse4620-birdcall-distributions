<script>
  import NavBar from "$lib/NavBar.svelte";

  export let data;
  $: client_status = data && data.client_status;
</script>

<NavBar {client_status} />

<slot />
