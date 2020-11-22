<template slot="my-link" slot-scope="data">
  <div id="app">
    <div id="query">
      <img
        id="twitterimg"
        src="https://www.creativefreedom.co.uk/wp-content/uploads/2017/06/Twitter-featured.png"
      />
      <h1>Twitter Tweet Analysis</h1>
      <input type="text" v-model="name" id="term" placeholder="Keyword" />
      <button v-on:click="analyzeTweets">Analyze</button>
    </div>
    <div id="data-table">
      <b-table
        id="data"
        striped
        hover
        bordered
        :items="items"
        :per-page="perPage"
        :current-page="currentPage"
      >
        <template #cell(url)="data">
          <span v-html="data.value"></span>
        </template>
      </b-table>
      <b-pagination
        id="pagination"
        v-model="currentPage"
        align="center"
        :total-rows="rows"
        :per-page="perPage"
        aria-controls="data"
      ></b-pagination>
    </div>

    <b-table id="stats-table" fixed striped hover bordered :items="stats">
    </b-table>
    <div id="graph-view">
      <div id="graph">
        <p>Graph is loading...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { DataSet, DataView } from "vis-data";
import { Network } from "vis-network";

export default {
  name: "app",
  data() {
    return {
      perPage: 5,
      currentPage: 1,
      items: [],
      stats: [],
    };
  },
  computed: {
    rows() {
      return this.items.length;
    },
  },
  methods: {
    showTable: function () {
      var z = document.getElementById("data-table");
      z.style.display = "block";
    },
    toggleHide: function () {
      var x = document.getElementById("graph");
      x.style.display = "flex";
    },
    truncate: function (input) {
      if (input.length > 200) {
        return input.substring(0, 200) + "...";
      }
      return input;
    },
    /**
     * Picks the color for an entity type
     */
    getColor: function (type) {
      switch (type) {
        case "PERSON":
          return "#373F51";
        case "TITLE":
          return "#008DD5";
        case "ORGANIZATION":
          return "#DFBBB1";
        case "OTHER":
          return "#F56476";
        case "LOCATION":
          return "#E43F6F";
        case "COMMERCIAL_ITEM":
          return "#A24936";
        case "EVENT":
          return "#83BCA9";
        default:
          return "#FFFFFF";
      }
    },
    /**
     * Renders the vis.js network graph
     */
    startGraph: function (data) {
      const container = document.querySelector("#graph");
      const options = {
        nodes: {
          shape: "box",
        },
        physics: {
          barnesHut: {
            damping: 0.25,
          },
        },
        groups: {
          PERSON: {
            color: "#373F51",
          },
          TITLE: {
            color: "#008DD5",
          },
          ORGANIZATION: {
            color: "#DFBBB1",
          },
          OTHER: {
            color: "#F56476",
          },
          LOCATION: {
            color: "#E43F6F",
          },
          COMMERCIAL_ITEM: {
            color: "#A24936",
          },
          EVENT: {
            color: "#83BCA9",
          },
        },
      };

      new Network(container, data, options);
    },
    /**
     * Retrieves the entities for the queried term and prepares the graph
     */
    async prepareGraph() {
      var ref = this;
      const term = document.querySelector("#term").value.trim();

      if (!term) {
        alert("No blanks");
        return;
      }

      const GET_GRAPH_URL = process.env.VUE_APP_GET_GRAPH_URL;

      try {
        const resp = await fetch(GET_GRAPH_URL, {
          method: "POST",
          body: term,
        });

        const entities = await resp.json();
        console.log(entities);

        // Hardcoded for now, the query to aws returns all of the entities from Neptune for "Pokemon"
        const nodes = new DataSet([
          {
            id: 0,
            label: document.querySelector("#term").value.toUpperCase().trim(),
            color: "#EF8354",
            font: {
              color: "white",
            },
          },
        ]);

        const edges = new DataSet([]);

        for (let i = 0; i < entities.length; i++) {
          const entity = entities[i];
          const entityNode = {
            id: i + 1,
            label: entity.value,
            color: ref.getColor(entity.type),
            group: entity.type,
            font: {
              color: "white",
            },
          };

          nodes.add(entityNode);
          edges.add({
            from: entityNode.id,
            to: 0,
            label: "has_entity",
            color: {
              color: "#606060",
            },
            width: 1,
          });
        }

        // Build legend last
        const LEGEND_TYPES = [
          "PERSON",
          "TITLE",
          "ORGANIZATION",
          "OTHER",
          "LOCATION",
          "COMMERCIAL_ITEM",
          "EVENT",
        ];

        const graph = document.getElementById("graph");
        const x = -graph.clientWidth / 2;
        const y = -graph.clientHeight / 2;
        const step = 100;

        for (let i = 0; i < LEGEND_TYPES.length; i++) {
          let yValue = y;

          if (i == 0) {
            yValue = y;
          } else {
            yValue += i * step;
          }

          nodes.add({
            id: nodes.length + i + 1,
            x: x,
            y: yValue,
            label: LEGEND_TYPES[i],
            group: LEGEND_TYPES[i],
            shape: "square",
            value: 1,
            physics: false,
            fixed: true,
          });
        }

        const nodesView = new DataView(nodes);
        const edgesView = new DataView(edges);

        ref.startGraph({
          nodes: nodesView,
          edges: edgesView,
        });
      } catch (e) {
        alert("Error building graph");
        console.log(e);
      }
    },
    /**
     * Retrieves tweets and Comprehend results, populates them into table
     */
    async analyzeTweets() {
      var ref = this;
      this.items = [];
      this.stats = [];

      document.getElementById("graph").innerHTML = "Graph is loading...";

      const ANALYZE_URL = process.env.VUE_APP_ANALYZE_URL;

      try {
        const response = await fetch(ANALYZE_URL, {
          method: "POST",
          body: document.querySelector("#term").value.trim(),
        });

        const items = await response.json();
        let formattedItems = [];
        console.log(items);

        let sentiment_score_accum = 0;
        let negative_count = 0;
        let positive_count = 0;
        let neutral_count = 0;

        items.forEach(function (entry) {
          if (entry.sentiment == "NEGATIVE") {
            negative_count++;
          } else if (entry.sentiment == "POSITIVE") {
            positive_count++;
          } else if (entry.sentiment == "NEUTRAL") {
            neutral_count++;
          }

          const url = "https://" + entry.url;
          const sentiment_score =
            Math.round(entry.sentiment_score * 100).toFixed(2) / 100;
          sentiment_score_accum += sentiment_score;

          var entity_string = entry.entities.map((x) => x.entity).join(", ");

          formattedItems.push({
            url: '<a href="' + url + '"target="_blank"> Link </a>',
            user: entry.user,
            tweet: entry.tweet,
            sentiment: entry.sentiment,
            sentiment_score: sentiment_score,
            entities: entity_string,
          });
        });

        console.log(formattedItems);

        this.items = formattedItems;
        ref.showTable();
        this.stats = [
          {
            average_sentiment_score: (
              sentiment_score_accum / items.length
            ).toFixed(3),
            Neutral_Occurences: neutral_count,
            Positive_Occurences: positive_count,
            Negative_Occurences: negative_count,
          },
        ];

        setTimeout(() => {
          ref.prepareGraph();
        }, 6500);
        ref.toggleHide();
      } catch (e) {
        alert("Error with request");
        console.log(e);
      }
    },
  },
};
</script>

<style scoped>
#data {
  padding: 10px;
}

#query {
  padding: 30px;
}

#stats-table {
  margin-left: auto;
  margin-right: auto;
  width: auto;
}
#data-table {
  display: none;
}
#graph {
  display: none;
  width: 1500px;
  height: 1000px;
  margin-left: auto;
  margin-right: auto;
  border: solid;
}
td,
th {
  border: 1px solid;
  text-align: left;
  padding: 8px;
}

#table-head {
  border: 1px solid;
  text-align: left;
  padding: 8px;
}

#twitterimg {
  width: 3.5%;
  float: left;
}
</style>
