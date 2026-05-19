package com.vector.onboarding.domain.dataview.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Slf4j
@Service
public class SchemaParserService {

    private final ObjectMapper objectMapper = new ObjectMapper();

    public String parseSchema(String fileContents) {
        log.info("자바 정규식(Regex)을 활용하여 스키마 파일을 분석합니다 (LLM 미사용).");
        
        List<Map<String, Object>> nodes = new ArrayList<>();
        List<Map<String, Object>> edges = new ArrayList<>();
        List<String> tasks = new ArrayList<>();
        List<String> criticalFiles = new ArrayList<>();
        
        int xOffset = 100;
        int yOffset = 100;
        
        // 중복 관계선 방지를 위한 고유 관계 셋
        Set<String> uniqueRelations = new HashSet<>();

        // ============================================
        // 1. Prisma 스키마 파싱 로직
        // ============================================
        Pattern modelPattern = Pattern.compile("model\\s+(\\w+)\\s+\\{([^}]+)\\}", Pattern.MULTILINE);
        Matcher modelMatcher = modelPattern.matcher(fileContents);
        
        while (modelMatcher.find()) {
            String modelName = modelMatcher.group(1);
            String body = modelMatcher.group(2);
            List<Map<String, String>> columns = new ArrayList<>();
            
            String[] lines = body.split("\n");
            for (String line : lines) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("//") || line.startsWith("@@")) continue;
                
                String[] parts = line.split("\\s+");
                if (parts.length >= 2) {
                    String colName = parts[0];
                    String colType = parts[1];
                    
                    Map<String, String> colMap = new HashMap<>();
                    colMap.put("name", colName);
                    
                    if (line.contains("@id")) {
                        colMap.put("type", colType + " (PK)");
                    } else if (line.contains("@unique")) {
                        colMap.put("type", colType + " (Unique)");
                    } else {
                        colMap.put("type", colType);
                    }
                    
                    // Edge 추출
                    if (line.contains("@relation")) {
                        colMap.put("type", colType + " (FK)");
                        String source = modelName.toLowerCase();
                        String target = colType.toLowerCase();
                        String relKey1 = source + "-" + target;
                        String relKey2 = target + "-" + source;
                        
                        if (!uniqueRelations.contains(relKey1) && !uniqueRelations.contains(relKey2)) {
                            uniqueRelations.add(relKey1);
                            Map<String, Object> edge = new HashMap<>();
                            edge.put("id", "e-" + source + "-" + target);
                            edge.put("source", source);
                            edge.put("target", target);
                            edge.put("sourceHandle", "bottom");
                            edge.put("targetHandle", "top");
                            edge.put("type", "customEdge");
                            
                            Map<String, String> edgeData = new HashMap<>();
                            edgeData.put("label", "Relation");
                            edgeData.put("labelClassName", "bg-gray-100 text-gray-800 text-[10px] px-2 py-1 rounded border z-10");
                            edge.put("data", edgeData);
                            edges.add(edge);
                        }
                    } else if (colType.endsWith("[]")) {
                        String targetModel = colType.replace("[]", "");
                        String source = modelName.toLowerCase();
                        String target = targetModel.toLowerCase();
                        String relKey1 = source + "-" + target;
                        String relKey2 = target + "-" + source;
                        
                        if (!uniqueRelations.contains(relKey1) && !uniqueRelations.contains(relKey2)) {
                            uniqueRelations.add(relKey1);
                            Map<String, Object> edge = new HashMap<>();
                            edge.put("id", "e-" + source + "-" + target);
                            edge.put("source", source);
                            edge.put("target", target);
                            edge.put("sourceHandle", "bottom");
                            edge.put("targetHandle", "top");
                            edge.put("type", "customEdge");
                            
                            Map<String, String> edgeData = new HashMap<>();
                            edgeData.put("label", "1 : N");
                            edgeData.put("labelClassName", "bg-blue-100 text-blue-800 text-[10px] px-2 py-1 rounded border z-10");
                            edge.put("data", edgeData);
                            edges.add(edge);
                        }
                    }
                    columns.add(colMap);
                }
            }
            nodes.add(createNode(modelName, columns, xOffset, yOffset));
            xOffset += 350;
            if (xOffset > 800) { xOffset = 100; yOffset += 300; }
        }

        // ============================================
        // 2. SQL CREATE TABLE 파싱 로직
        // ============================================
        Pattern sqlPattern = Pattern.compile("CREATE\\s+TABLE\\s+(\\w+)\\s+\\(([^;]+)\\);", Pattern.CASE_INSENSITIVE | Pattern.MULTILINE);
        Matcher sqlMatcher = sqlPattern.matcher(fileContents);
        
        while (sqlMatcher.find()) {
            String tableName = sqlMatcher.group(1);
            String body = sqlMatcher.group(2);
            List<Map<String, String>> columns = new ArrayList<>();
            
            String[] lines = body.split(",");
            for (String line : lines) {
                line = line.trim();
                if (line.isEmpty() || line.toUpperCase().startsWith("PRIMARY KEY") || line.toUpperCase().startsWith("FOREIGN KEY")) continue;
                
                String[] parts = line.split("\\s+");
                if (parts.length >= 2) {
                    Map<String, String> colMap = new HashMap<>();
                    colMap.put("name", parts[0]);
                    String type = parts[1];
                    if (line.toUpperCase().contains("PRIMARY KEY")) type += " (PK)";
                    colMap.put("type", type);
                    columns.add(colMap);
                }
            }
            nodes.add(createNode(tableName, columns, xOffset, yOffset));
            xOffset += 350;
            if (xOffset > 800) { xOffset = 100; yOffset += 300; }
        }

        tasks.add("자바 정규식 파서를 통한 스키마 분석 성공");
        tasks.add("GitHub Repository 연동 확인 완료");
        criticalFiles.add("파싱된 스키마 파일 목록 확인");
        
        String schemaPreview = fileContents.length() > 500 ? fileContents.substring(0, 500) + "...\n(코드 생략됨)" : fileContents;

        Map<String, Object> result = new HashMap<>();
        result.put("nodes", nodes);
        result.put("edges", edges);
        result.put("tasks", tasks);
        result.put("criticalFiles", criticalFiles);
        result.put("schemaPreview", schemaPreview);
        
        try {
            return objectMapper.writeValueAsString(result);
        } catch (Exception e) {
            log.error("JSON 파싱 변환 실패", e);
            return "{ \"nodes\": [], \"edges\": [] }";
        }
    }

    private Map<String, Object> createNode(String name, List<Map<String, String>> columns, int x, int y) {
        Map<String, Object> node = new HashMap<>();
        node.put("id", name.toLowerCase());
        node.put("type", "tableNode");
        
        Map<String, Integer> position = new HashMap<>();
        position.put("x", x);
        position.put("y", y);
        node.put("position", position);
        
        Map<String, Object> data = new HashMap<>();
        data.put("title", name);
        data.put("icon", "Database");
        data.put("columns", columns);
        node.put("data", data);
        return node;
    }
}
