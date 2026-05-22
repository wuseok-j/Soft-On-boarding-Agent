package com.vector.onboarding.domain.dataview.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vector.onboarding.domain.dataview.entity.DataView;
import com.vector.onboarding.domain.dataview.entity.SchemaAnalysisResult;
import com.vector.onboarding.domain.dataview.repository.DataViewRepository;
import com.vector.onboarding.domain.dataview.repository.SchemaAnalysisResultRepository;
import com.vector.onboarding.domain.space.Space;
import com.vector.onboarding.domain.space.SpaceRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class DataViewService {

    private final DataViewRepository dataViewRepository;
    private final SchemaAnalysisResultRepository schemaAnalysisResultRepository;
    private final GithubFileFetchService githubFileFetchService;
    private final SchemaParserService schemaParserService;
    private final SpaceRepository spaceRepository;
    private final ObjectMapper objectMapper;

    /**
     * 특정 spaceId의 전체 데이터에 대한 스키마를 제공합니다.
     * 캐시가 존재하면 병합하여 반환하고, 미분석된 파일이 있는 경우 온디맨드로 분석해 캐싱을 업데이트한 후 병합합니다.
     */
    @Transactional
    public String getOrAnalyzeSchema(Long spaceId) {
        Space space = spaceRepository.findById(spaceId)
                .orElseThrow(() -> new IllegalArgumentException("스페이스를 찾을 수 없습니다."));
        String repositoryUrl = space.getRepoUrl();

        List<DataView> dataViews = dataViewRepository.findAllBySpaceId(spaceId);

        if (dataViews.isEmpty()) {
            log.warn("DB에 데이터(DataView)가 없습니다. spaceId: {}, repositoryUrl: {}", spaceId, repositoryUrl);
            return "{ \"nodes\": [], \"edges\": [] }";
        }

        // 각 파일별 캐시를 검사하고 미분석된 파일은 온디맨드로 즉시 파싱 (안전 장치)
        for (DataView dataView : dataViews) {
            String filePath = dataView.getFilePath();
            if (filePath == null || filePath.isEmpty()) {
                continue;
            }

            Optional<SchemaAnalysisResult> cached = schemaAnalysisResultRepository
                    .findFirstBySpaceIdAndFilePathOrderByIdDesc(spaceId, filePath);
            boolean needsAnalysis = true;
            if (cached.isPresent()) {
                String cachedJson = cached.get().getAnalyzedJson();
                boolean isEmptyCache = cachedJson == null || cachedJson.trim().isEmpty();
                if (!isEmptyCache) {
                    needsAnalysis = false;
                }
            }

            if (needsAnalysis) {
                log.info("온디맨드 캐시 빌드: 미분석된 파일을 발견하여 즉시 파싱을 실행합니다. file: {}", filePath);
                try {
                    analyzeAndSaveSingleFile(spaceId, repositoryUrl, filePath);
                } catch (Exception e) {
                    log.error("온디맨드 파일 분석 실패 - filePath: " + filePath, e);
                }
            }
        }

        // 전체 레코드 다시 조회 후 병합
        List<SchemaAnalysisResult> results = schemaAnalysisResultRepository.findAllBySpaceId(spaceId);
        return mergeSchemaJsons(results);
    }

    /**
     * 특정 스페이스의 한 파일에 대해 단독으로 분석을 수행하고 DB에 캐싱합니다.
     */
    @Transactional
    public SchemaAnalysisResult analyzeAndSaveSingleFile(Long spaceId, String repositoryUrl, String filePath) {
        log.info("파일 개별 스키마 분석 시작 - spaceId: {}, filePath: {}", spaceId, filePath);
        String content = githubFileFetchService.fetchFileContent(repositoryUrl, filePath);
        String analyzedJson = schemaParserService.parseSchema(content, filePath);

        Optional<SchemaAnalysisResult> existing = schemaAnalysisResultRepository
                .findFirstBySpaceIdAndFilePathOrderByIdDesc(spaceId, filePath);
        String dummyCommitHash = "fetched-at-" + System.currentTimeMillis();

        SchemaAnalysisResult result;
        if (existing.isPresent()) {
            result = existing.get();
            result.updateAnalysis(dummyCommitHash, analyzedJson);
        } else {
            result = SchemaAnalysisResult.builder()
                    .spaceId(spaceId)
                    .filePath(filePath)
                    .repositoryUrl(repositoryUrl)
                    .commitHash(dummyCommitHash)
                    .analyzedJson(analyzedJson)
                    .build();
        }
        return schemaAnalysisResultRepository.save(result);
    }

    /**
     * 특정 스페이스에 대한 미분석 데이터들을 백그라운드 스레드에서 비동기 분석 및 사전 캐싱합니다.
     */
    @Async
    @Transactional
    public void preloadAndCacheForSpaceAsync(Long spaceId) {
        log.info("비동기 사전 캐싱 요청 수신 - spaceId: {}", spaceId);
        Optional<Space> spaceOpt = spaceRepository.findById(spaceId);
        if (spaceOpt.isEmpty()) {
            log.warn("비동기 사전 캐싱 실패: 스페이스 정보가 존재하지 않습니다. spaceId: {}", spaceId);
            return;
        }

        String repositoryUrl = spaceOpt.get().getRepoUrl();
        if (repositoryUrl == null || repositoryUrl.isEmpty()) {
            log.warn("비동기 사전 캐싱 실패: 스페이스의 레포지토리 URL이 없습니다. spaceId: {}", spaceId);
            return;
        }

        List<DataView> dataViews = dataViewRepository.findAllBySpaceId(spaceId);
        for (DataView dataView : dataViews) {
            String filePath = dataView.getFilePath();
            if (filePath == null || filePath.isEmpty())
                continue;

            Optional<SchemaAnalysisResult> cached = schemaAnalysisResultRepository
                    .findFirstBySpaceIdAndFilePathOrderByIdDesc(spaceId, filePath);
            boolean needsAnalysis = true;
            if (cached.isPresent()) {
                String cachedJson = cached.get().getAnalyzedJson();
                boolean isEmptyCache = cachedJson == null || cachedJson.trim().isEmpty();
                if (!isEmptyCache) {
                    needsAnalysis = false;
                }
            }

            if (needsAnalysis) {
                try {
                    analyzeAndSaveSingleFile(spaceId, repositoryUrl, filePath);
                    log.info("비동기 사전 캐싱 성공 - spaceId: {}, filePath: {}", spaceId, filePath);
                } catch (Exception e) {
                    log.error("비동기 사전 캐싱 실패 - spaceId: {}, filePath: {}, error: {}", spaceId, filePath, e.getMessage());
                }
            }
        }
    }

    /**
     * 전체 스페이스에 대해 미분석 파일이 존재하면 백그라운드 스레드에서 사전 캐싱합니다. (앱 구동 시 호출용)
     */
    @Async
    @Transactional
    public void preloadAndCacheAllSpacesAsync() {
        log.info("비동기 전체 스페이스 사전 캐싱을 수행합니다.");
        List<Space> spaces = spaceRepository.findAll();
        for (Space space : spaces) {
            try {
                preloadAndCacheForSpaceAsync(space.getId());
            } catch (Exception e) {
                log.error("스페이스 비동기 사전 캐싱 실패 - spaceId: " + space.getId(), e);
            }
        }
    }

    /**
     * 여러 SchemaAnalysisResult 레코드들의 개별 JSON을 읽어 하나의 { nodes, edges } 구조로 병합하고
     * 서로 다른 파일 간의 상관관계(Cross-file Relations)를 동적으로 분석하여 Edge를 추가합니다.
     */
    @SuppressWarnings("unchecked")
    public String mergeSchemaJsons(List<SchemaAnalysisResult> results) {
        Map<String, Object> mergedNodes = new LinkedHashMap<>();
        Map<String, Object> mergedEdges = new LinkedHashMap<>();

        // 1. 각 파일의 개별 노드/엣지 파싱 병합
        for (SchemaAnalysisResult result : results) {
            String json = result.getAnalyzedJson();
            if (json == null || json.trim().isEmpty())
                continue;
            try {
                Map<String, Object> map = objectMapper.readValue(json, Map.class);
                List<Map<String, Object>> nodes = (List<Map<String, Object>>) map.get("nodes");
                List<Map<String, Object>> edges = (List<Map<String, Object>>) map.get("edges");

                if (nodes != null) {
                    for (Map<String, Object> node : nodes) {
                        String id = (String) node.get("id");
                        if (id != null) {
                            mergedNodes.put(id, node);
                        }
                    }
                }

                if (edges != null) {
                    for (Map<String, Object> edge : edges) {
                        String id = (String) edge.get("id");
                        if (id != null) {
                            mergedEdges.put(id, edge);
                        }
                    }
                }
            } catch (Exception e) {
                log.error("병합 도중 JSON 파싱 실패 - result id: " + result.getId(), e);
            }
        }

        // 2. 교차 파일 상관관계(Cross-file Relations) 분석 및 추가 Edge 생성
        Set<String> uniqueRelations = new HashSet<>();

        // 기존에 이미 존재하는 Edge들을 uniqueRelations에 등록하여 중복을 방지
        for (Object edgeObj : mergedEdges.values()) {
            Map<String, Object> edge = (Map<String, Object>) edgeObj;
            String src = (String) edge.get("source");
            String tgt = (String) edge.get("target");
            if (src != null && tgt != null) {
                uniqueRelations.add(src.toLowerCase() + "-" + tgt.toLowerCase());
                uniqueRelations.add(tgt.toLowerCase() + "-" + src.toLowerCase()); // 양방향 중복 방지
            }
        }

        // 전체 노드 맵을 순회하며 외래 키(FK) 및 참조 관계 유추
        for (Map.Entry<String, Object> entry : mergedNodes.entrySet()) {
            String currentId = entry.getKey().toLowerCase(); // 소문자 테이블/클래스명
            Map<String, Object> node = (Map<String, Object>) entry.getValue();
            Map<String, Object> data = (Map<String, Object>) node.get("data");
            if (data == null)
                continue;

            List<Map<String, String>> columns = (List<Map<String, String>>) data.get("columns");
            if (columns == null)
                continue;

            String currentTitle = (String) data.get("title");

            for (Map<String, String> col : columns) {
                String colName = col.get("name") != null ? col.get("name").toLowerCase() : "";
                String colType = col.get("type") != null ? col.get("type").toLowerCase() : "";

                // 모든 다른 테이블과 비교
                for (String otherId : mergedNodes.keySet()) {
                    if (currentId.equals(otherId))
                        continue;

                    Map<String, Object> otherNode = (Map<String, Object>) mergedNodes.get(otherId);
                    Map<String, Object> otherData = (Map<String, Object>) otherNode.get("data");
                    String otherTitle = otherData != null ? (String) otherData.get("title") : otherId;

                    boolean isRelation = false;
                    String source = null;
                    String target = null;
                    String label = null;

                    // A. SQL/JPA FK 컬럼명 컨벤션 유추 (예: 현재 컬럼이 member_id 이고, 상대 테이블이 member인 경우)
                    if (!colType.equals("source") &&
                            (colName.equals(otherId + "id") ||
                                    colName.equals(otherId + "_id") ||
                                    colName.equals(otherId + "sid") ||
                                    colName.equals(otherId + "_sid") ||
                                    colName.equals(otherId + "s_id") ||
                                    colName.equals(otherId + "s_sid"))) {

                        isRelation = true;
                        source = otherId;
                        target = currentId;
                        label = col.get("name") + ":" + otherTitle;

                        // 컬럼 타입에 (FK) 표시 추가
                        if (!col.get("type").contains("(FK)")) {
                            col.put("type", col.get("type") + " (FK)");
                        }
                    }
                    // B. JPA 객체 참조 타입 유추 (예: 현재 컬럼 타입이 Member 이고, 상대 테이블이 member인 경우)
                    else if (colType.replace(" (fk)", "").trim().equals(otherId)) {
                        isRelation = true;
                        source = otherId;
                        target = currentId;
                        label = col.get("name") + ":" + otherTitle;

                        // 컬럼 타입에 (FK) 표시 추가
                        if (!col.get("type").contains("(FK)")) {
                            col.put("type", col.get("type") + " (FK)");
                        }
                    }
                    // C. JPA 컬렉션 일대다 참조 유추 (예: 현재 컬럼 타입이 List<Order> 이고, 상대 테이블이 order인 경우)
                    else if (colType.contains("list<" + otherId + ">") ||
                            colType.contains("set<" + otherId + ">") ||
                            colType.equals(otherId + "[]")) {

                        isRelation = true;
                        source = currentId;
                        target = otherId;
                        label = col.get("name") + ":" + otherTitle;
                    }

                    // 관계가 성립하고, 아직 존재하지 않는 Edge인 경우 생성
                    if (isRelation && source != null && target != null) {
                        String relKey1 = source.toLowerCase() + "-" + target.toLowerCase();
                        String relKey2 = target.toLowerCase() + "-" + source.toLowerCase();

                        if (!uniqueRelations.contains(relKey1) && !uniqueRelations.contains(relKey2)) {
                            uniqueRelations.add(relKey1);
                            uniqueRelations.add(relKey2);

                            Map<String, Object> newEdge = new HashMap<>();
                            String edgeId = "e-" + source + "-" + target;
                            newEdge.put("id", edgeId);
                            newEdge.put("source", source);
                            newEdge.put("target", target);
                            newEdge.put("sourceHandle", "bottom");
                            newEdge.put("targetHandle", "top");
                            newEdge.put("type", "customEdge");

                            Map<String, String> edgeData = new HashMap<>();
                            edgeData.put("label", label);

                            // 스타일 구분 (컬렉션 기반 1:N 이나 Array는 파란색, 일반 FK는 회색)
                            if (label.contains("[]") || colType.contains("list") || colType.contains("set")) {
                                edgeData.put("labelClassName",
                                        "bg-blue-50 text-blue-700 text-[10px] font-medium px-2 py-1 rounded border border-blue-200 shadow-sm z-10");
                            } else {
                                edgeData.put("labelClassName",
                                        "bg-gray-50 text-gray-700 text-[10px] font-medium px-2 py-1 rounded border border-gray-200 shadow-sm z-10");
                            }
                            newEdge.put("data", edgeData);

                            mergedEdges.put(edgeId, newEdge);
                        }
                    }
                }
            }
        }

        Map<String, Object> finalResult = new HashMap<>();
        finalResult.put("nodes", new ArrayList<>(mergedNodes.values()));
        finalResult.put("edges", new ArrayList<>(mergedEdges.values()));

        try {
            return objectMapper.writeValueAsString(finalResult);
        } catch (Exception e) {
            log.error("병합 데이터 직렬화 실패", e);
            return "{ \"nodes\": [], \"edges\": [] }";
        }
    }
}
