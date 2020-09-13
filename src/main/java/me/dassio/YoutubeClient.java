package me.dassio;

import java.util.Arrays;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Profile;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.ModelAndView;
import com.google.api.client.googleapis.auth.oauth2.GoogleAuthorizationCodeRequestUrl;
import com.google.api.client.auth.oauth2.AuthorizationCodeResponseUrl;
import com.google.api.client.googleapis.auth.oauth2.GoogleAuthorizationCodeTokenRequest;
import com.google.api.client.googleapis.auth.oauth2.GoogleTokenResponse;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.jackson2.JacksonFactory;
import com.google.api.client.auth.oauth2.TokenResponseException;
import com.google.api.client.googleapis.auth.oauth2.GoogleCredential;
import java.io.IOException;
import javax.servlet.http.HttpServletRequest;

import com.google.api.services.youtube.YouTube;
import com.google.api.client.googleapis.javanet.GoogleNetHttpTransport;
import com.google.api.client.json.JsonFactory;
import com.google.api.client.googleapis.json.GoogleJsonResponseException;
import com.google.api.services.youtube.model.ChannelListResponse;

import java.security.GeneralSecurityException;

@RestController
@Profile("dev")
class YoutubeClient {


	private static final JsonFactory JSON_FACTORY = JacksonFactory.getDefaultInstance();

	@Autowired
	private CredentialRepository repository;

	@Value("${applicationName}")
	private String applicationName;
	@Value("${youtube.clientId}")
	private String clientId;
	@Value("${youtube.clientSecret}")
	private String clientSecret;
	@Value("${youtube.apiKey}")
	private String apiKey;
	@Value("${youtube.redirectUrl}")
	private String redirectUrl;

	@GetMapping("/authen")
	public ModelAndView doGet() {
		String url = new GoogleAuthorizationCodeRequestUrl(clientId,
				redirectUrl,Arrays.asList(
					"https://www.googleapis.com/auth/youtube.force-ssl"
					))
			.setApprovalPrompt("force")
			.setAccessType("offline")
			.build();
		return new ModelAndView("redirect:"+url);
	}

	@GetMapping("/access-token")
	public String doGetAccesstoken(HttpServletRequest request) {
		String result = "";
		String fullUrl = request.getRequestURL().toString() + "?" + request.getQueryString();
		AuthorizationCodeResponseUrl authResponse =
			new AuthorizationCodeResponseUrl(fullUrl);
		// check for user-denied error
		if (authResponse.getError() != null) {
			return authResponse.getError();
		} else {
			try {
				GoogleTokenResponse response =
					new GoogleAuthorizationCodeTokenRequest(new NetHttpTransport(), new JacksonFactory(),
							clientId, clientSecret,
							authResponse.getCode(), redirectUrl)
					.execute();
				repository.save(new Credential( response.getAccessToken(),response.getRefreshToken()));
				return response.toString();
			} catch (TokenResponseException e) {
				if (e.getDetails() != null) {
					result = "Error: " + e.getDetails().getError();
					if (e.getDetails().getErrorDescription() != null) {
						result  +=  e.getDetails().getErrorDescription();
					}
					if (e.getDetails().getErrorUri() != null) {
						result += e.getDetails().getErrorUri();
					}
				} else {
					result += e.getMessage();
				}
			} catch (IOException e) {
					result += e.getMessage();
			}
		}
		return result;
	}

	@GetMapping("/channels")
	public ChannelListResponse getChannels() throws GeneralSecurityException, IOException, GoogleJsonResponseException {
		YouTube youtubeService = getService();
		YouTube.Channels.List request = youtubeService.channels().list("brandingSettings");
		ChannelListResponse response = request.setMine(true).execute();
		return response;
	}

	private  YouTube getService() throws GeneralSecurityException, IOException {
		final NetHttpTransport httpTransport = GoogleNetHttpTransport.newTrustedTransport();

		GoogleCredential googleCredential = new GoogleCredential.Builder()
			.setTransport(httpTransport)
			.setJsonFactory(JSON_FACTORY)
			.setClientSecrets(clientId,clientSecret)
			.build();
		Optional<Credential> testuser = repository.findById(new Integer(2));
		testuser.ifPresent(user -> {
			googleCredential.setAccessToken(user.getAccessToken());
			googleCredential.setRefreshToken(user.getRefreshToken());
		});
		return new YouTube.Builder(httpTransport, JSON_FACTORY, googleCredential)
			.build();
	}
}
