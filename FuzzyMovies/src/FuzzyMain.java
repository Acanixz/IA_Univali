import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

public class FuzzyMain {
	public static void main(String[] args) {
		System.out.println("Rodando codigo do trabalho");
		
		String movieGenres = "Terror, Suspense, Fantasia, Music";
        float result = fuzzyGenreMatch(movieGenres);
        System.out.println("Relevância total: " + result);
		
        GrupoVariaveis grupoGenero = new GrupoVariaveis();
        grupoGenero.add(new VariavelFuzzy("Genero Irrelevante", 0, 0, 10, 20));
        grupoGenero.add(new VariavelFuzzy("Genero Pouco Relevante", 10, 20, 30, 60));
        grupoGenero.add(new VariavelFuzzy("Genero Relevante", 20, 40, 50, 70));
        grupoGenero.add(new VariavelFuzzy("Genero Muito Relevante", 40, 60, 70, 120));
        
        GrupoVariaveis grupoKeywords = new GrupoVariaveis();
        grupoKeywords.add(new VariavelFuzzy("Keywords Irrelevantes", 0, 0, 10, 20));
        grupoKeywords.add(new VariavelFuzzy("Keywords Pouco Relevantes", 10, 20, 30, 60));
        grupoKeywords.add(new VariavelFuzzy("Keywords Relevantes", 20, 40, 50, 70));
        grupoKeywords.add(new VariavelFuzzy("Keywords Muito Relevantes", 40, 60, 70, 120));
        
        
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
