import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


public class FuzzyMain {
	private static class Movie {
	    String title;
	    String genres;
	    String keywords;
	    float score;

	    public Movie(String title, String genres, String keywords, float score) {
	        this.title = title;
	        this.genres = genres;
	        this.keywords = keywords;
	        this.score = score;
	    }
	}
	
	
	public static void main(String[] args) {
		System.out.println("Rodando codigo do trabalho");
		List<Movie> moviesList = new ArrayList<>();
		
        GrupoVariaveis grupoGenero = new GrupoVariaveis();
        grupoGenero.add(new VariavelFuzzy("Genero Irrelevante", -100, 0, 0, (float) 0.1));
        grupoGenero.add(new VariavelFuzzy("Genero Pouco Relevante", (float) 0.0, (float) 0.1, (float) .5, (float) .75));
        grupoGenero.add(new VariavelFuzzy("Genero Relevante", (float) .5, (float) .75, (float) .8, (float) 1));
        grupoGenero.add(new VariavelFuzzy("Genero Muito Relevante", (float) .9, (float) .95, (float) .95, (float) 100));
        
        GrupoVariaveis grupoKeywords = new GrupoVariaveis();
        grupoKeywords.add(new VariavelFuzzy("Keywords Irrelevantes", 0, 0, 1, (float) 1.5));
        grupoKeywords.add(new VariavelFuzzy("Keywords Pouco Relevantes", 1, 2, 2, (float) 2.5));
        grupoKeywords.add(new VariavelFuzzy("Keywords Relevantes", 2, 3, (float) 3.5, 4));
        grupoKeywords.add(new VariavelFuzzy("Keywords Muito Relevantes", 4, (float) 4.5, 10, 10));
        
        try {
			BufferedReader bfr = new BufferedReader(new FileReader(new File("FuzzyMovies/movie_dataset.csv")));
			
			String header = bfr.readLine();
			String splitheder[] = header.split(";");
			for (int i = 0; i < splitheder.length;i++) {
				System.out.println(""+i+" "+splitheder[i]);
			}
			
			String line = "";
			
			while((line=bfr.readLine())!=null) {
				String spl[] = line.split(";");
				HashMap<String,Float> asVariaveis = new HashMap<String,Float>();
				
				String genero = spl[2];
				grupoGenero.fuzzifica(fuzzyGenreMatch(genero), asVariaveis);
				
				String keywords = spl[5];
				grupoKeywords.fuzzifica(fuzzyKeywordMatch(keywords), asVariaveis);
				
				
				System.out.println(""+spl[7]+" - generos: "+genero+" palavras-chave: "+ keywords);
				
				
				rodaRegraE(asVariaveis,"Genero Irrelevante", "Keywords Irrelevantes", "Irrelevante");
				rodaRegraE(asVariaveis,"Genero Irrelevante", "Keywords Pouco Relevantes", "Irrelevante");
				rodaRegraE(asVariaveis,"Genero Irrelevante", "Keywords Relevantes", "Irrelevante");
				rodaRegraE(asVariaveis,"Genero Irrelevante", "Keywords Muito Relevantes", "Relevante");
				
				rodaRegraE(asVariaveis,"Genero Pouco Relevante", "Keywords Irrelevantes", "Irrelevante");
				rodaRegraE(asVariaveis,"Genero Pouco Relevante", "Keywords Pouco Relevantes", "Irrelevante");
				rodaRegraE(asVariaveis,"Genero Pouco Relevante", "Keywords Relevantes", "Relevante");
				rodaRegraE(asVariaveis,"Genero Pouco Relevante", "Keywords Muito Relevantes", "Relevante");
				
				rodaRegraE(asVariaveis,"Genero Relevante", "Keywords Irrelevantes", "Irrelevante");
				rodaRegraE(asVariaveis,"Genero Relevante", "Keywords Pouco Relevantes", "Relevante");
				rodaRegraE(asVariaveis,"Genero Relevante", "Keywords Relevantes", "Muito Relevante");
				rodaRegraE(asVariaveis,"Genero Relevante", "Keywords Muito Relevantes", "Muito Relevante");
				
				rodaRegraE(asVariaveis,"Genero Muito Relevante", "Keywords Irrelevantes", "Relevante");
				rodaRegraE(asVariaveis,"Genero Muito Relevante", "Keywords Pouco Relevantes", "Muito Relevante");
				rodaRegraE(asVariaveis,"Genero Muito Relevante", "Keywords Relevantes", "Muito Relevante");
				rodaRegraE(asVariaveis,"Genero Muito Relevante", "Keywords Muito Relevantes", "Muito Relevante");
				
				float Irrelevante = asVariaveis.get("Genero Irrelevante");
				float Relevante = asVariaveis.get("Relevante");
				float MuitoRelevante = asVariaveis.get("Muito Relevante");
				
				float score = (Irrelevante*1.5f+Relevante*7.0f+MuitoRelevante*9.5f)/(Irrelevante+Relevante+MuitoRelevante);
				
				// Trata casos onde nenhum genero alvo foi mencionado, resultando em NaN
				if (Float.isNaN(score)){
					score = -10;
				}
				
				System.out.println("Irrelevante: "+ Irrelevante+" Relevante: "+ Relevante +" Muito Relevante: "+ MuitoRelevante);
				System.out.println(" "+genero+" | "+keywords +"-> "+score);
				System.out.println(" ");
				
				Movie currentMovie = new Movie(spl[7], genero, keywords, score);
				moviesList.add(currentMovie);
			}
			// Ordena filmes em ordem descendente
			moviesList.sort((m1, m2) -> Float.compare(m2.score, m1.score));

			// Display TOP 10
			System.out.println("\n\n=== TOP 10 Filmes ===");
			int limit = Math.min(10, moviesList.size());
			for (int i = 0; i < limit; i++) {
			    Movie movie = moviesList.get(i);
			    System.out.printf("%d. %s (Score: %.2f)%n", i + 1, movie.title, movie.score);
			}
			
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	private static void rodaRegraE(HashMap<String, Float> asVariaveis,String var1,String var2,String varr) {
		float v = Math.min(asVariaveis.get(var1),asVariaveis.get(var2));
		if(asVariaveis.keySet().contains(varr)) {
			float vatual = asVariaveis.get(varr);
			asVariaveis.put(varr, Math.max(vatual, v));
		}else {
			asVariaveis.put(varr, v);
		}
	}
	
	private static void rodaRegraOU(HashMap<String, Float> asVariaveis,String var1,String var2,String varr) {
		float v = Math.max(asVariaveis.get(var1),asVariaveis.get(var2));
		if(asVariaveis.keySet().contains(varr)) {
			float vatual = asVariaveis.get(varr);
			asVariaveis.put(varr, Math.max(vatual, v));
		}else {
			asVariaveis.put(varr, v);
		}
	}
	
	//Função que avalia a relevância fuzzy dos generos
	private static float fuzzyGenreMatch(String genre) {
		// Relevancia inicial e normalização do campo
		float relevance = 0f;
		genre = genre.toLowerCase();
		
		// Cria um mapa de gêneros e seus respectivos pontos
	  Map<String, Float> genreMap = new HashMap<>();
	  genreMap.put("terror", 1f);
	  genreMap.put("suspense", 0.7f);
	  genreMap.put("thriller", 0.7f);
	  genreMap.put("mystery", 0.5f);
	  genreMap.put("fantasy", 0.5f);
	  genreMap.put("animation", 0.5f);
	  genreMap.put("science", .25f);
	  genreMap.put("crime", .25f);
	  genreMap.put("comedy", .1f);
	  
	  genreMap.put("family", -0.1f);
	  genreMap.put("documentary", -0.1f);
	  genreMap.put("romance", -0.25f);
	  genreMap.put("music", -10f);
	  

	  // Itera pelas entradas do mapa
	  for (Map.Entry<String, Float> entry : genreMap.entrySet()) {
	      // Se o gênero contiver o termo da chave, acumula a pontuação
	      if (genre.contains(entry.getKey())) {
	          relevance += entry.getValue();
	      }
	  }
	  
	  
	  return relevance;
	}
	
	//Função que avalia a relevância fuzzy das palavras-chave
		private static float fuzzyKeywordMatch(String keywords) {
		// Relevancia inicial e normalização do campo
		float relevance = 0f;
		keywords = keywords.toLowerCase();
		
		// Cria um mapa de palavras-chave e seus respectivos pontos
	  Map<String, Float> keywordMap = new HashMap<>();
	  keywordMap.put("murder", 1f);
	  keywordMap.put("killer", 1f);
	  keywordMap.put("psychopath", 1f);
	  keywordMap.put("slasher", .75f);
	  keywordMap.put("detective", .5f);
	  keywordMap.put("assassin", .5f);
	  keywordMap.put("blood", .25f);
	  keywordMap.put("gore", .25f);
	  keywordMap.put("hitman", .25f);
	  keywordMap.put("kidnapping", .1f);
	  

	  // Itera pelas entradas do mapa
	  for (Map.Entry<String, Float> entry : keywordMap.entrySet()) {
	      // Se o filme tiver uma das palavras-chave, acumula a pontuação
	      if (keywords.contains(entry.getKey())) {
	          relevance += entry.getValue();
	      }
	  }
	  
	  
	  return relevance;
	}
}
