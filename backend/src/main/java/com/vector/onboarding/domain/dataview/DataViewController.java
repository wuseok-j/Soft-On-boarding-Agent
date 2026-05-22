package com.vector.onboarding.domain.dataview;

import com.vector.onboarding.domain.dataview.service.DataViewService;
import com.vector.onboarding.domain.space.Space;
import com.vector.onboarding.domain.space.SpaceRepository;
import com.vector.onboarding.domain.space.SpaceService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/spaces/{spaceId}/data-view")
@RequiredArgsConstructor
public class DataViewController {

    private final DataViewService dataViewService;
    private final SpaceService spaceService;
    private final SpaceRepository spaceRepository;

    @GetMapping(value = "/schema", produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getSchema(
            @AuthenticationPrincipal UserDetails userDetails,
            @PathVariable Long spaceId) {

        Long requestUserId = Long.valueOf(userDetails.getUsername());
        spaceService.checkSpaceMembership(requestUserId, spaceId);

        Space space = spaceRepository.findById(spaceId)
                .orElseThrow(() -> new IllegalArgumentException("스페이스를 찾을 수 없습니다."));
        String schemaJson = dataViewService.getOrAnalyzeSchema(space.getRepoUrl());
        return ResponseEntity.ok(schemaJson);
    }
}
